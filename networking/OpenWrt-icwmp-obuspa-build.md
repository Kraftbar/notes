# Building icwmp (TR-069) + obuspa (TR-369/USP) for OpenWrt
Done 2026-09-19 for the Netgear R7800 on OpenWrt 23.05.5. Neither agent is in the OpenWrt
feeds; both come from the IOPSYS feed and need the SDK. Build on `lat` (Docker), install with
`opkg` — no firmware flash involved, `firstboot` is the undo.

## Which feed branch
`https://dev.iopsys.eu/feed/iopsys.git` branch `devel`. Their release branches are iopsysWrt
versions (3.x–7.x), not OpenWrt ones. `devel` pins the `packages` feed to a commit on
`openwrt-23.05`, so it matches a 23.05.x router. Check before trusting:
```sh
curl -s https://dev.iopsys.eu/iopsys/iopsyswrt/-/raw/devel/feeds.conf.default | grep packages
# then: is that commit on openwrt-23.05?
curl -s https://api.github.com/repos/openwrt/packages/compare/openwrt-23.05...<sha> | grep status
# "behind" = yes (ancestor of the branch head). "diverged" = wrong release line.
```

## The build
The official SDK image `openwrt/sdk:ipq806x-generic-23.05.5` is Debian 11 — **LTS ended
2026-08-31, `apt-get` is dead inside it**. Anything the host needs gets copied in as a binary.
```sh
mkdir -p ~/icwmp-build && cd ~/icwmp-build
curl -sfL -o jq https://github.com/jqlang/jq/releases/download/jq-1.7.1/jq-linux-amd64 && chmod +x jq
printf 'FROM openwrt/sdk:ipq806x-generic-23.05.5\nCOPY jq /usr/local/bin/jq\n' > Dockerfile
docker build -t openwrt-sdk-jq .
docker volume create owrt-sdk-state         # /builder is a VOLUME in the image - see gotchas
docker run --name owrt-sdk -v owrt-sdk-state:/builder -v "$PWD/out:/out" openwrt-sdk-jq bash -c '
  cd /builder
  echo "src-git iopsys https://dev.iopsys.eu/feed/iopsys.git;devel" >> feeds.conf.default
  ./scripts/feeds update -a && ./scripts/feeds install icwmp obuspa
  # obuspa insists on an OpenSSL-backed libcurl; 23.05 default is mbedTLS
  sed -i "/^CONFIG_LIBCURL_MBEDTLS=/d" .config; echo "CONFIG_LIBCURL_OPENSSL=y" >> .config
  make defconfig
  make package/icwmp/compile package/obuspa/compile package/curl/compile -j$(nproc)
  cp -r bin/packages /out/'
```
Output: `out/packages/<arch>/iopsys/*.ipk` (9 files, ~1.2 MB) plus the rebuilt `libcurl4` under
`out/packages/<arch>/base/` (or `packages/`).

## Gotchas hit, in order
1. **`bbfdm` fails packaging `dm-service` with "Invalid datamodel json input file".** The JSON is
   fine; `bbfdm/tools/bbfdm.sh` pipes it through `jq`, which the SDK image lacks. Hence the
   `jq` in the Dockerfile above.
2. **obuspa fails to download: `fatal: reference is not a tree: e80f6dc…`.** The feed pins a
   commit that is no longer on any branch. `git clone` + `checkout` can't reach it, but a
   direct SHA fetch can. Pre-seed the tarball OpenWrt expects, then the build skips the clone:
   ```sh
   SHA=e80f6dcea3f108817fd7f946d3608da4cd43ef66
   mkdir -p tmp/dl/obuspa-11.0.7.4 && cd tmp/dl/obuspa-11.0.7.4
   git init -q && git fetch -q --depth 1 https://dev.iopsys.eu/bbf/obuspa.git $SHA && git checkout -q FETCH_HEAD
   TS=$(git log -1 --format=@%ct); cd ..; rm -rf obuspa-11.0.7.4/.git
   tar --numeric-owner --owner=0 --group=0 --mode=a-s --sort=name --mtime="$TS" -c obuspa-11.0.7.4 \
     | zstd -T0 -c > /builder/dl/obuspa-11.0.7.4-$SHA.tar.zst
   ```
   (`PKG_MIRROR_HASH:=skip`, so any valid tarball with that name is accepted.)
3. **The SDK image declares `VOLUME /builder`.** Two consequences: `docker commit` snapshots an
   *empty* tree (volume contents are never committed), and `docker rm` without `-v` leaves the
   real 2.5 GB of state as a dangling anonymous volume. Always mount a **named** volume from the
   start. If you already lost it: `docker volume ls -qf dangling=true`, then mount each into
   `alpine` and look for `/m/.config` + `/m/feeds/iopsys`.
4. **Runtime: obuspa aborts with `Failed to select OpenSSL backend for libcurl`.** Both the
   router's stock `libcurl4` and the SDK's default build are mbedTLS. Rebuild curl with
   `CONFIG_LIBCURL_OPENSSL=y` and `opkg install --force-reinstall` it. Same `libcurl4` ABI.
5. **`opkg install /tmp/libcurl4_*.ipk` silently installed the *feed's* libcurl4 instead.**
   Same name and version in the index, so opkg preferred the index. Nothing in the output says
   so. Hide the lists for that one install, and verify on the `.so`, not on `opkg status`
   (its Depends line stayed stale afterwards):
   ```sh
   mv /var/opkg-lists /var/opkg-lists.off
   opkg install --force-reinstall /tmp/libcurl4_*.ipk
   mv /var/opkg-lists.off /var/opkg-lists
   grep -c libssl /usr/lib/libcurl.so.4*     # 1 = OpenSSL backend live
   ```
6. **`make` inside a detached container must never reach `menuconfig`.** If `.config` is missing
   it tries to, and dies with `Error opening terminal: unknown`. That's the symptom of gotcha 3.

## Install on the router
Stock OpenWrt has no `sftp-server`, so modern `scp` fails — use legacy mode (`-O`).
```sh
ssh owrt 'sysupgrade -b /tmp/pre-icwmp.tar.gz'; scp -O owrt:/tmp/pre-icwmp.tar.gz ./   # backup first
ssh owrt 'mkdir -p /tmp/ipk'; scp -O out/packages/*/iopsys/*.ipk owrt:/tmp/ipk/
ssh owrt 'cd /tmp/ipk && opkg update && opkg install ./*.ipk'   # standard deps come from the 23.05 feed
scp -O out/packages/*/base/libcurl4_*.ipk owrt:/tmp/; ssh owrt 'opkg install --force-reinstall /tmp/libcurl4_*.ipk'
```
Expect postinst noise: `db: not found`, `get_serial_number: not found`, `uci: Parse error`.
That's IOPSYS assuming its own firmware (`db` is their board database). Harmless — the daemons
start anyway, you just set identity by hand (below). ~14 MB of overlay.

## Configure icwmp
Ships with `dhcp_discovery enable` and **no ACS URL** — it waits for DHCP option 43 like an ISP
CPE would. `Device.DeviceInfo.Manufacturer` etc. are empty without `db`, and icwmpd refuses to
Inform without them; the README documents these overrides:
```sh
uci set cwmp.acs.url='http://192.168.1.223:7547/cwmp'
uci set cwmp.acs.dhcp_discovery='disable'
uci set cwmp.cpe.manufacturer='Netgear'
uci set cwmp.cpe.manufacturer_oui='A00460'          # first 6 hex of the MAC
uci set cwmp.cpe.product_class='R7800'
uci set cwmp.cpe.serial_number='A0046017BDCB'       # MAC without colons; no readable serial
uci set cwmp.cpe.software_version='OpenWrt 23.05.5'
uci set cwmp.cpe.model_name='Nighthawk X4S R7800'
uci commit cwmp && /etc/init.d/icwmpd restart
logread -f | grep cwmp     # Start session -> Inform -> InformResponse -> 204 -> End session
```

## Configure obuspa
IOPSYS's init script builds obuspa's factory-reset file from UCI sections of type `localagent`,
`controller`, `mtp`, `mqtt`, `stomp`, `subscription`, `challenge`. Option names are the data-model
names. For the agent as a **WebSocket client** to a controller (the mock runs the WS server):
```sh
uci batch <<'EOT'
set obuspa.global.dhcp_discovery=0
set obuspa.localagent=localagent
set obuspa.localagent.EndpointID=os::A00460-A0046017BDCB
set obuspa.controller_mockacs=controller
set obuspa.controller_mockacs.Enable=1
set obuspa.controller_mockacs.EndpointID=os::mockacs
set obuspa.controller_mockacs.Protocol=WebSocket
set obuspa.controller_mockacs.Host=192.168.1.223
set obuspa.controller_mockacs.Port=7548
set obuspa.controller_mockacs.Path=/usp
set obuspa.controller_mockacs.EnableEncryption=0
set obuspa.controller_mockacs.assigned_role_name=full_access
commit obuspa
EOT
/etc/init.d/obuspa restart; logread | grep obuspa
```
Two log lines that look like failures and aren't: `No enabled MTPs in Device.LocalAgent.MTP`
(that's the agent's *server-side* MTP — not needed when the agent is the WebSocket client) and
one `Discarding USP message to send to controller.1.MTP.1` before the socket is up. Success looks
like this in the controller's log: `websocket_connect` record → `NOTIFY` `OnBoardRequest` →
`NOTIFY_RESP`. Check with `obuspa -c get Device.LocalAgent.Controller.1.` on the router.

Trust roles shipped in `/etc/obuspa/ctrust_reset`: `full_access`, `Untrusted` (the default if
`assigned_role_name` is omitted — the controller can then do nothing useful), `extender`.

## The controller side
`lat:/var/www/twitterclone/tools/mockacs` (Go, no deps). It binds `127.0.0.1` by default;
the router is another host, so bind the LAN address — not `0.0.0.0`, lat may be internet-reachable:
```sh
go build -o ~/icwmp-build/mockacs . && ~/icwmp-build/mockacs -http 192.168.1.223:7547 -usp 192.168.1.223:7548
```
Admin (`:7557`) and XMPP (`:5222`) stay on loopback.

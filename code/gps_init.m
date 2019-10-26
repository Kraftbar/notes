clear all
close all


%%
fac  = 1;
hsiz = fac*210;
vsiz = fac*297;

%% Sample time
T = 1;

%% Disturbance model
tau = 200; q = 15^2;

Ac = [0 0 1 0;0 0 0 1;0 0 -1/tau 0; 0 0 0 -1/tau];
Gc = [0 0;0 0;1/tau 0;0 1/tau];
Qc = q*eye(2);

% Loan method
S = Gc*Qc*Gc'; H = [Ac S; zeros(4) -Ac']; M = expm(H*T);
A = M(1:4,1:4); Q = M(1:4,5:8)*A';

% Diagonalization
[VQ,DQ] = eig(Q); % Q = VQ*DQ*VQ'
sig = sqrt(diag(DQ));

%% Measurement model

sv = 5;
Rc = sv^2*eye(2);
C  = [1 0 0 0;0 1 0 0]; 

R  = Rc/T;

%% Simulate
K = 3600; ks = 0:(K-1);

x  = zeros(4,1); 

% Initialize a-priori state and covariance matrix
xm = zeros(4,1); Pm =  [3.8720         0    0.3254         0;
                             0    3.8720         0    0.3254;
                        0.3254         0    0.0589         0;
                             0    0.3254         0    0.0589];

L_hist=ones(4,2,3600);
P_hist=ones(4,4,3600);

for k = 1:K
    %% Collect measurement
    y = C*x + normrnd(zeros(2,1),sv);
    
    %% Kalman filter
    %(1) Kalman gain
    L = Pm*C'*inv(C*Pm*C'+R);
    L_hist(:,:,k)=L;
    %(2) Update estimate
    xh = xm + L*(y-C*xm);
    %(3) Update covariance
    P = (eye(4)-L*C)*Pm*(eye(4)-L*C)' + L*R*L';
    P_hist(:,:,k)=P;
    %(4) Project ahead
    xm = A*xh; Pm = A*P*A'+Q;
    
    %% Store data
    X(:,k) = x; Xh(:,k) = xh; Y(:,k) = y;
    
    %% Model update
    x = A*x + VQ*normrnd(zeros(4,1),sig);  
      
end

b = figure;
plot(Y(1,:),Y(2,:),'.g',X(1,:),X(2,:),'k',Xh(1,:),Xh(2,:),'r'); 
xlabel('$p_1[m]$','interpreter','latex');ylabel('$p_2[m]$','interpreter','latex'); 
title('Random walk'); grid on;
h = legend('$y[m]$','$p[m]$','$\hat{p}[m]$'); set(h,'interpreter','latex'); 
axis equal

%set(b,'Renderer', 'painters','position',[200 200 2*hsiz vsiz],'PaperPositionMode','auto')
%print('-dpng','-r600','/Users/morten/Documents/FAG/TTK4115/2016/Lectures/Lecture_K/pics/gps_p_3')


b = figure;
plot(ks,3.6*sqrt(X(3,:).^2+X(4,:).^2),'k',ks,3.6*sqrt(Xh(3,:).^2+Xh(4,:).^2),'r'); 
xlabel('$t$','interpreter','latex'); 
h = legend('$|\dot{p}|[km/h]$','$|\dot{\hat{p}}|[km/h]$'); title('Speed estimate');
set(h,'interpreter','latex');

%set(b,'Renderer', 'painters','position',[200 200 2*hsiz vsiz],'PaperPositionMode','auto')
%print('-dpng','-r600','/Users/morten/Documents/FAG/TTK4115/2016/Lectures/Lecture_K/pics/gps_v');



%% P AND L are not magic!
% values are dependent on initial  

% plot hist
figure 

hold on 
for i=1:4
for j=1:4
title("Historical value of P")
plot(reshape(P_hist(i,j,:),[],1))
end
end
P_hist(:,:,end)

% plot matrix
figure 
title("Historical value of L")
hold on 
for i=1:4
for j=1:2
plot(reshape(L_hist(i,j,:),[],1))
end
end
% checking values
L_hist(:,:,end)


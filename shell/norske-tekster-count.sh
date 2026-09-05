IF NOT "%PROCESSOR_ARCHITECTURE%" == "x86" (
  # Check for input arguments
  if ($args.Count -ne 2) {
    Write-Host "Usage: scriptname.ps1 word file"
    exit
  }
  # Set the word and file variables
  $word = $args[0]
  $file = $args[1]
  # Use Select-String to count the occurrences of the word in the file
  $count = (Select-String -Path $file -Pattern $word -AllMatches).Matches.Count
  # Print the result
  Write-Host "The word '$word' appears $count times in the file $file"
) ELSE (
  # Check for input arguments
  if [ $# -ne 2 ]; then
    echo "Usage: $0 word file"
    exit 1
  fi
  # Set the word and file variables
  word=$1
  file=$2
  # Use grep to count the occurrences of the word in the file
  count=$(grep -o $word $file | wc -l)
  # Print the result
  echo "The word '$word' appears $count times in the file $file"
)

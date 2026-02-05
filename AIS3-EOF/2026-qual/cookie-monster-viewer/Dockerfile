FROM python:3.12-windowsservercore-ltsc2022

WORKDIR /supersecureyouwillneverguessed

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .

# First move the flag (while we have write access)
SHELL ["powershell", "-Command"]
RUN $rand = -join ((65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_}); Move-Item C:\supersecureyouwillneverguessed\flag.txt C:\flag-$rand.txt; attrib +R (Get-Item C:\flag-*.txt).FullName

# Then lock down permissions
SHELL ["cmd", "/S", "/C"]
RUN net user /add appuser && \
    attrib +R C:\supersecureyouwillneverguessed\*.* /S && \
    icacls C:\supersecureyouwillneverguessed /grant appuser:(OI)(CI)(RX) /T && \
    icacls C:\supersecureyouwillneverguessed /deny appuser:(WD,AD,DC)

USER appuser
CMD ["python", "app.py"]
FROM ubuntu.azurecr.io/ubuntu:22.10 AS builder

# install the .NET 6 SDK from the Ubuntu archive
# (no need to clean the apt cache as this is an unpublished stage)
RUN apt-get update && apt-get install -y dotnet6 ca-certificates

# add your application code
WORKDIR /source
COPY src/ .

# publish your .NET app
RUN dotnet publish -c Release -o /app

FROM ubuntu.azurecr.io/dotnet-runtime:6.0-22.04_beta

WORKDIR /app
COPY --from=builder /app ./

EXPOSE 8080

ENTRYPOINT ["dotnet", "/app/Hello.dll"]

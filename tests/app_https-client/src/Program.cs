using System;
using System.Net.Http;

HttpClient hc = new HttpClient(new HttpClientHandler { ClientCertificateOptions = ClientCertificateOption.Automatic });
Console.WriteLine(hc.GetStringAsync("https://httpbin.org/ip").GetAwaiter().GetResult());

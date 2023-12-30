// IMPORT NECESSARY PACKAGES -------------------------------------------------------------------------------------------------------------
// Before you start, please install the following packages in Visual Studio Code via e.g. Terminal. For this, run the following commands:
// dotnet add package Azure.DigitalTwins.Core
// dotnet restore
// dotnet add package Azure.Messaging.EventGrid
// dotnet restore

using System;
using Azure;
using System.Net.Http;
using Azure.Core.Pipeline;
using Azure.DigitalTwins.Core;
using Azure.Identity;
using Microsoft.Azure.WebJobs;
using Microsoft.Azure.WebJobs.Extensions.EventGrid;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Azure.Messaging.EventGrid;
using System.Text;

// ------------------------------------------------------------------------------------------------------------------------------------------

namespace IotHubtoTwins
{
    public class IoTHubtoTwins
    {
        private static readonly string adtInstanceUrl = Environment.GetEnvironmentVariable("ADT_SERVICE_URL");
        private static readonly HttpClient httpClient = new HttpClient();

        [FunctionName("IoTHubtoTwins")]
        // While async void should generally be used with caution, it's not uncommon for Azure function apps, since the function app isn't awaiting the task.
#pragma warning disable AZF0001 // Suppress async void error
        public async void Run([EventGridTrigger] EventGridEvent eventGridEvent, ILogger log)
#pragma warning restore AZF0001 // Suppress async void error
        {
            if (adtInstanceUrl == null) log.LogError("Application setting \"ADT_SERVICE_URL\" not set");

            try
            {
                // Authenticate with Digital Twins
                var cred = new DefaultAzureCredential();
                var client = new DigitalTwinsClient(new Uri(adtInstanceUrl), cred);
                log.LogInformation($"ADT service client connection created.");
            
                if (eventGridEvent != null && eventGridEvent.Data != null)
                {

                    // Log all Data
                    log.LogInformation(eventGridEvent.Data.ToString());

                    // 1. Load all Data into Object deviceMessage
                    JObject deviceMessage = (JObject)JsonConvert.DeserializeObject(eventGridEvent.Data.ToString());

                    // 2. Read the device id
                    string deviceId = (string)deviceMessage["systemProperties"]["iothub-connection-device-id"];
                    log.LogInformation($"Device-ID: {deviceId}");

                    // 3. Encode Body of deviceMessage to get all measured sensor-data (Temperature and Humidity)
                    var decodedBytes = Convert.FromBase64String(deviceMessage["body"].ToString());
                    var encodedBody = Encoding.UTF8.GetString(decodedBytes);
                    log.LogInformation($"JSON-String: {encodedBody}");

                    // 4. Read Measured sensor-data into variables
                    dynamic payloadObject = JsonConvert.DeserializeObject(encodedBody);
                    double temperature = payloadObject.Temperature;
                    double humidity = payloadObject.Humidity;
                    log.LogInformation($"Temperatur: {temperature} Humidity: {humidity}");

                    // 5. Send Data to Azure Digital Twins
                    var updateTwinData = new JsonPatchDocument();
                    updateTwinData.AppendReplace("/Temperature", temperature);
                    updateTwinData.AppendReplace("/Humidity", humidity);
                    await client.UpdateDigitalTwinAsync(deviceId, updateTwinData);

                }
            }
            catch (Exception ex)
            {
                log.LogError($"Error in ingest function: {ex.Message}");
            }
        }
    }
}
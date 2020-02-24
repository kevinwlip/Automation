var mockServerCli = require('mockserver-client'),
    mockServerClient = mockServerCli.mockServerClient; // MockServer client

mockServerClient("localhost", 8888)
    .mockAnyResponse({
    "httpRequest": {
      "method": "GET",
      "path": "/ers/config/endpoint",
      "queryStringParameters": {
        "filter": ["mac.EQ.00:23:68:E3:FB:19"]
      },
      "headers":
      {
        "Accept": ["application/json"],
        "Authorization": ["Basic YWRtaW46MklTRTRaaW5nYm94"],
        "Cache-Control": ["no-cache"]
      }
    },
    "httpResponse": 
    {
      "body": JSON.stringify({ "SearchResult": { "total": 1, "resources": [ { "id": "e871f300-78d1-11e8-a58b-f2ee6b21cb4e", "name": "00:23:68:E3:FB:19", "link": { "rel": "self", "href": "https://192.168.20.72:9060/ers/config/endpoint/e871f300-78d1-11e8-a58b-f2ee6b21cb4e", "type": "application/xml" } } ] } } )
    }
  })
    .then(
        function(result) {
            console.log("expectation created");
        }, 
        function(error) {
            console.log(error);
        }
    );


mockServerClient("localhost", 8888)
    .mockAnyResponse({
    "httpRequest": {
      "method": "GET",
      "path": "/ers/config/endpoint2",
      "queryStringParameters": {
        "filter": ["mac.EQ.00:23:68:E3:FB:19"]
      },
      "headers":
      {
        "Accept": ["application/json"],
        "Authorization": ["Basic YWRtaW46MklTRTRaaW5nYm94"],
        "Cache-Control": ["no-cache"]
      }
    },
    "httpResponse": 
    {
      "body": JSON.stringify({ "SearchResult2": { "total": 1, "resources": [ { "id": "e871f300-78d1-11e8-a58b-f2ee6b21cb4e", "name": "00:23:68:E3:FB:19", "link": { "rel": "self", "href": "https://192.168.20.72:9060/ers/config/endpoint/e871f300-78d1-11e8-a58b-f2ee6b21cb4e", "type": "application/xml" } } ] } } )
    }
  })
    .then(
        function(result) {
            console.log("expectation created");
        }, 
        function(error) {
            console.log(error);
        }
    );
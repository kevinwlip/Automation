var mockServerCli = require('mockserver-client'),
    mockServerClient = mockServerCli.mockServerClient, // MockServer client
    proxyClient = mockServerCli.proxyClient;

var mockserver = require('mockserver-node');

var glob = require( 'glob' )
  , path = require( 'path' );



function content(){
    mockServerClient("localhost", 8888)
    .mockAnyResponse({
    "httpRequest": {
      "method": "GET",
      "path": "/view/cart"
    },
    "httpResponse": {
      "body": "some_response_body"
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
    
    glob.sync( './*.js' ).forEach( function( file ) {
  require( path.resolve( file ) );
});
}


async function clean_start(){
    const server_start= await mockserver.start_mockserver({
                serverPort: 8888,
                verbose: true
            });
    
    const content_create = await content(server_start);
    console.log('Press any key to exit');

}

async function clean_exit(){
    const userInfo = await mockserver.stop_mockserver({
                serverPort: 8888,
                verbose: true
            });
    const orderInfo = await process.exit(userInfo);
    return orderInfo;
}
 


 
// do something

clean_start();

process.stdin.setRawMode(true);
process.stdin.resume();

process.stdin.on('data', function()
    {
        clean_exit()
    });

    
 


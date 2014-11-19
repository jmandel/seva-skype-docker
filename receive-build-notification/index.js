var http = require('http');
var request = require('request');
var port = process.env.PORT || 5556;
var secret = process.env.SECRET || "changeme";
var sevaurl = process.env.SEVA_URL || "http://localhost:5000/message_unsigned/";
var chatid = process.env.SEVA_CHAT || "a-chat-id";

var messageForStatus = [ "Passed", "Fixed", "Broken", "Still Failing" ];
var failedStatus = [ "Broken", "Still Failing" ];

var server = http.createServer(function (req, response) {
  if (req.url  !== "/notify/"+secret){
    console.log('Bad secret on build notification');
    response.statusCode = 401;
    return response.end();
  }
  console.log('Build notification', { url: req.url });
  var data = '';
  req.on('data', function (chunk) {
    data += chunk;
  });
  req.on('end',function(){
    var n = JSON.parse(data);
    console.log("msg", n.status_message);
    if (messageForStatus.indexOf(n.status_message) !== -1) {
      var emote = ":-)";
      if (failedStatus.indexOf(n.status_message) !== -1) {
        emote = ":-(";
      }
      var message = "Build status: " + n.status_message + " " + emote + " For commit by " + n.author_email ;
      console.log("Messaging: " , message);
      request.post(sevaurl, {form:{chat_id:chatid, message: message}}, function(){
        response.end();
      });
    }

  });
});

if (port) {
  server.listen(port);
}

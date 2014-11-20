var http = require('http');
var request = require('request');
var port = process.env.PORT || 5556;
var secret = process.env.SECRET || "changeme";
var sevaurl = process.env.SEVA_URL || "http://localhost:5000/message_unsigned/";
var chatid = process.env.SEVA_CHAT || "a-chat-id";
var decode = require('querystring').parse;

var messageForStatus = [ "Fixed", "Broken", "Still Failing" ]; // not "Passed"
var failedStatus = [ "Broken", "Still Failing" ];

var server = http.createServer(function (req, response) {

  var auth = req.headers.authorization && req.headers.authorization.trim();
  
  console.log('Build notification', { url: req.url, 'head': req.headers});
  if (req.url  !== "/notify/status" || auth !== secret){
    console.log('Bad secret on build notification');
    response.statusCode = 401;
    return response.end();
  }

  var data = '';
  req.on('data', function (chunk) {
    data += chunk;
  });
  req.on('end',function(){
    var form = decode(data);
    var n = JSON.parse(form && form.payload);
    console.log("msg", n.status_message);
    var author = n.author_email.split("@")[0]; 
    var svnrev = n.message.match(/(@\d{3,})/g);
    svnrev = svnrev && svnrev[0] || "??";

    if (messageForStatus.indexOf(n.status_message) !== -1) {
      var emote = ":-)";
      if (failedStatus.indexOf(n.status_message) !== -1) {
        emote = ":-(";
      }
      var message = "Build status: " + n.status_message + " " +
                    emote + " For commit " + svnrev + " by " + author;

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

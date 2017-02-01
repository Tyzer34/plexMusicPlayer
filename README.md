# Plex Music Player
Full blog post available on: https://medium.com/@Tyzer34/plex-alexa-the-perfect-wedding-38b14b41faf0#.b71cd6lsn

The purpose of this project is to give Alexa users a way to playback music, using their own Plex server. However, it is also a way to show developers a method to integrate Plex into Alexa as a music service. The application does however not enable remote control of Plex instances, nor does it (as for this moment) include a global technique of authentication. However, a detailed overview on how to setup this application is provided below.

As a developer, I wanted to broaden the spectrum a bit by giving Alexa users access to their own Plex Music Player. Heroku is used for the deployment of the application, but almost any platform can be used. Do keep in mind that deployment on PythonAnywhere will not work for this application, as their whitelist does not allow access to the Plex servers.

**Note that this skill is not made by nor supported by Plex!**
## The Setup
First, you should have Heroku and Git installed on your local machine. If you have not yet worked with Heroku before, the installation process can be found here. Also, make sure that you are already logged in with Heroku account.

Next, we want to clone the current GitHub repository of this project. First, open up a terminal (or command prompt) and navigate to the directory you want the files to be stored in. Then, use the following command to clone the repo.
```
git clone https://github.com/tyzer34/plexmusicplayer.git
```
Now that the files have been cloned locally, they can be deployed on Heroku. To set up this Heroku server, the following commands should be used. Note that *yourServerName* should be replaced by something else.
```
heroku create *yourServerName*
git push heroku master
```
The application should normally be online now! Now we just have to set the authentication variables on the server and set up the Alexa Skill.

### Getting Plex Authentication Variables

In order to authenticate the PlexMusicPlayer application, two environmental variables need to be set, namely the Plex token and the base url. 

First, you will need to navigate to plex.tv/web/app, select a random episode, show, etc. and click the three dots on the left (as shown in the picture below in Dutch). Next, right click the Download option and select copy link address.

The copied link address form should normally look something like this (with the parts filled in though):
```
https://your-plex-ip-address.some_long_encoded_string.plex.direct:your_plex_port/library/parts/some_id/some_file_id/file.ext?download=1&X-Plex-Token=your_plex_token
```
When looking at this long url, both needed variables can be extracted as following. It is important for the base url that the / after your_plex_port is not copied with.
```
base url = https://your-plex-ip-address.some_long_encoded_string.plex.direct:your_plex_port
Plex token = your_plex_token
```
Now, we have to set these environmental variables in our Heroku server. To do this, go back to the terminal (or command prompt) and enter the following lines, changed with your extracted variables.
```
heroku config:set PLEX_TOKEN=your_plex_token
heroku config:set PLEX_URL=https://your-plex-ip-address.some_long_encoded_string.plex.direct:your_plex_port
```
Lastly, we just have to restart the server so it can cope with the set environmental variables. To do this, just use the following command.
```
heroku restart
```

#### Optional Local URL Variable

If you choose to customise your setup and host Plex Music Player on the same network as your Plex server you can also set a PLEX_LOCAL_URL environment variable. This takes the same format as the PLEX_URL variable, but rather than using a publicly available URL for Plex it uses an address that is only accessible within the local network. This has the advantage of making searches much faster as they do not have to travel outside your network between different servers. The PLEX_URL variable still has to be set to a publicly available URL in order for Alexa to fetch the media being played.

```
export PLEX_LOCAL_URL=https://192.168.*.*.some_long_encoded_string.plex.direct:your_plex_port
```

192.168.*.* would be replaced by the IP address of the machine on which your Plex server is hosted.

### Making the Alexa Skill
Now that the backend is fully up and running, the Alexa Skill has to be initialized on Amazon Developers. If you have not done this before, you can follow [this step-by-step explenation](https://blog.craftworkz.co/flask-ask-a-tutorial-on-a-simple-and-easy-way-to-build-complex-alexa-skills-426a6b3ff8bc#0acf).

As for the invocation name, I chose plexmusic. However, this can be anything you want. The information needed to fill in the Intent Schema and Sample Utterances can be found in the speech_assets folder.

Next, the endpoint needs to be set to HTTPS with the following link (with the *yourServerName* changed to the previously selected one)
```
https://*yourServerName*.herokuapp.com/plex
```
Lastly, select the 2nd option at certificate for endpoint and save your application.

Congratulations! PlexMusicPlayer is now up and running on your favorite Alexa device(s). Now, you are ready to try out some of its functionalities!

##The Functionalities
Currently, PlexMusicPlayer is able to playback music based on a provided artist, album or song title. When an artist or album is provided and multiple songs are available for that artist or album in your Plex library, these will be queued and played as a playlist. Furthermore, it is possible to ask information related to the current song or to shuffle the current playlist. Obviously, requests such as next and play are also implemented. Some activation sentences are provided as an example below.
```
Alexa, ask plexmusic to play Def Leppard.
Alexa, ask plexmusic to play the album AM by Arctic Monkeys.
Alexa, ask plexmusic to tell me the name of this song.
Alexa, ask plexmusic to play “my favorites” playlist.
```

##The Future
As this is only an initial implementation, there is a lot of room for improvement and extra functionality. Below is a list of some of the things I’d like to see implemented in the project. Please note that there is no distinction between minor and major improvements in these examples.
- Enabling user authentication based on a Plex PIN ([node.js](https://github.com/overloadut/node-plex-api-pinauth) implementation)
- Implementing more playback functionalities, such as playback based on genre or year
- Adding Alexa cards to show the requested song, album or artist with a picture
- Making more intents, so the user can request specific actions such as what year the song is from
Tracking of these future implementations are provided in the projects tab. User contributions and improvements are also welcome!

Hopefully, this guide was able to allow music playback from your Plex Media Server on Echo devices. If there are any issues or questions, please do not hesitate to open up an issue on GitHub.

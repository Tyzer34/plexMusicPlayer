from flask_ask import audio, statement, question
from plexmusicplayer import ask, queue, app
from plexmusicplayer.utils import Track, QueueManager, MediaType

# --------------------------------------------------------------------------------------------
# Amazon Playback - Intents

@ask.launch
def new_ask():
    welcome = "Welcome to the Plex Music Player. What would you like to hear?"
    reprompt = "I did not quite catch that. Could you repeat that please?"
    return question(welcome) \
        .reprompt(reprompt)

@ask.on_playback_stopped()
def stopped(offset):
    queue._current.set_offset(offset)
    app.logger.debug("Playback stopped at %s" % offset)

@ask.on_playback_started()
def started(offset):
    app.logger.debug("Playback started at %s" % offset)

@ask.on_playback_nearly_finished()
def nearly_finished():
    global queue
    if queue.up_next:
        return audio().enqueue(queue.up_next.stream_url)

@ask.on_playback_finished()
def play_back_finished():
    global queue
    if queue.up_next:
        queue.step()

@ask.intent('AMAZON.NextIntent')
def next_song():
    global queue
    if queue.up_next:
        return audio("").play(queue.step().stream_url)
    else:
        return audio("").stop()

@ask.intent('AMAZON.PreviousIntent')
def previous_song():
    global queue
    if queue.previous:
        return audio("").play(queue.step_back().stream_url)
    else:
        return statement("")

@ask.intent('AMAZON.StartOverIntent')
def restart_track():
    global queue
    if queue.current:
        return audio("").play(queue.current, offset=0)

@ask.intent('AMAZON.PauseIntent')
def pause():
    return audio("").stop()

@ask.intent('AMAZON.ResumeIntent')
def resume():
    return audio("").play(queue._current.stream_url, offset=queue._current.offset)

@ask.intent('AMAZON.ShuffleOnIntent')
def shuffle():
    queue.shuffle()
    return statement("")

@ask.intent('AMAZON.StopIntent')
def stop():
    return audio('Goodbye').clear_queue(stop=True)

@ask.session_ended
def session_ended():
    return "", 200
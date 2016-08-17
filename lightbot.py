import os
import time
from slackclient import SlackClient
import opc

# starterbot's ID as an environment variable
#BOT_ID = os.environ.get("BOT_ID")
BOT_ID = "U1T9YNQKS"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

def red_alert():
    numLEDs = 251
    frequency = 0.5
    #Connect to light controller  
    client = opc.Client('10.0.100.6:80')

    for c in range(60): 
        # [ (red, green, blue) ]
        pixels = [ (255,0,0) ] * numLEDs #creates an array of all the pixels (the whole row)
        client.put_pixels(pixels)
        time.sleep(frequency)
        pixels = [ (0,0,0) ] * numLEDs 
        client.put_pixels(pixels)
        time.sleep(frequency)
    

def handle_command(command, channel):
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    print("Handling")
    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    if command.startswith("red alert"):
	response = "Initiating Red Alert!"
	red_alert()
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    print("Parsing %d messages") % len(output_list)
    if output_list and len(output_list) > 0:
        for output in output_list:
	    print (output)
	    if output and 'text' in output:
		if AT_BOT in output['text']:
			print ("FOUND IT")
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

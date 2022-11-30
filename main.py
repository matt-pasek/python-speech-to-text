import argparse
import requests
import time
import pyttsx3

# Mateusz Pasek & Maksymilian Rybak 3tc

# helper function to read file


def read_file(filename):
    with open(filename, "rb") as f:
        while True:
            # read 5MB (recommended by them) at a time to avoid memory issues
            data = f.read(5242880)
            if not data:
                break
            yield data

# main function


def main():
    upload_url = "https://api.assemblyai.com/v2/upload"
    transcript_url = "https://api.assemblyai.com/v2/transcript"

    # argument parsing eg. python main.py audio.mp3 --print --local
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_file")
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    # headers for the upload request, so they know who we are and what we're sending
    header = {
        "Content-Type": "application/json",
        # i know this is not a good practice but its just for testing
        "Authorization": '4fbfca28b5034a9ca4e4f35f79f88866',
    }

    # upload file to assemblyai either as a local file or as a url
    if args.local:
        upload_response = requests.post(
            upload_url, headers=header, data=read_file(args.audio_file))
        upload_url = upload_response.json()
    else:
        upload_url = {"upload_url": args.audio_file}

    # prepare url for transcript
    transcript_request = {"audio_url": upload_url["upload_url"]}
    transcript_response = requests.post(
        transcript_url, headers=header, json=transcript_request)
    polling_url = "https://api.assemblyai.com/v2/transcript/" + \
        transcript_response.json()["id"]

    # wait for the transcript to be ready
    while True:
        polling_response = requests.get(polling_url, headers=header)
        polling_response = polling_response.json()
        if polling_response["status"] == "completed":
            break
        time.sleep(3)

    # get the transcript and assemble it
    paragraphs_response = requests.get(
        polling_url + "/paragraphs", headers=header)
    transcript = []
    for paragraph in paragraphs_response.json()["paragraphs"]:
        transcript.append(paragraph)

    # if --print is specified, print the transcript, otherwise only save it to a file
    if args.print:
        with open("transcript.txt", "w") as f:
            for line in transcript:
                l = line["text"] + "\n"
                print(l)
                f.write(l)
    else:
        with open("transcript.txt", "w") as f:
            for line in transcript:
                l = line["text"] + "\n"
                f.write(l)

    # text to speech
    with open("transcript.txt", "r") as f:
        text = f.read()
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    return


if __name__ == "__main__":
    main()

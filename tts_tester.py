
from elevenlabs import play
from elevenlabs.client import ElevenLabs

client = ElevenLabs(
  api_key="de309d56bba6c2436b1df046ad337108", # Defaults to ELEVEN_API_KEY
)

audio = client.generate(
  text="What Do You Want Done With Your Remains After You Die? Fuck cremation. Shoot me out of a cannon into the ocean when I die. Stick my whole body in the thing, then blast me out to sea.Second choice: Cryogenic preservation. Stick me on ice, then try reviving me in 500 years. Hey, why TF not?",
  voice="Adam",
  model="eleven_multilingual_v2"
)
play(audio)

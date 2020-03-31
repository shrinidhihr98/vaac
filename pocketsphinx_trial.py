import os
from pocketsphinx import LiveSpeech, get_model_path

model_path = "vaac_model"

speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=os.path.join(model_path, 'vaac_model.cd_cont_2000'),
    lm=os.path.join(model_path, 'vaac_model.lm.DMP'),
    dic=os.path.join(model_path, 'vaac_model.dic')
)

for phrase in speech:
    print(phrase)

import librosa  # Optional. Use any library you like to read audio files.
import soundfile  # Optional. Use any library you like to write audio files.
import os
from slicer2 import Slicer


def process(fn, args=None, export_pth=None):
    if args is None:
        args = {}
    try:
        audio, sr = librosa.load(fn, sr=None, mono=False)  # Load an audio file with librosa.
    except Exception as err:
        print("Failed to load", fn, str(err))
        return
    if not args:
        args = {
            "threshold": -40,
            "min_length": 5000,
            "min_interval": 300,
            "hop_size": 10,
            "max_sil_kept": 500,
        }  # general config for slicing
    args["sr"] = sr
    # slicer = Slicer(
    #     sr=sr,
    #     threshold=-40,
    #     min_length=6000,
    #     min_interval=1000,
    #     hop_size=10,
    #     max_sil_kept=500
    # )
    slicer = Slicer(**args)
    sp = os.path.sep
    try:
        if not export_pth:
            os.mkdir(f".{sp}clips{sp}{fn.split(sp)[-1].split('.')[0]}")
            export_pth = f".{sp}clips{sp}{fn.split(sp)[-1].split('.')[0]}"
        else:
            try:
                os.mkdir(f".{sp}clips{sp}{export_pth}")
            except Exception:
                pass
            export_pth = f".{sp}clips{sp}{export_pth}"
    except Exception as err:
        print(str(err))
        return f"clips{sp}{fn.split(sp)[-1].split('.')[0]}"
    try:
        chunks = slicer.slice(audio)
        for i, chunk_r in enumerate(chunks):
            chunk, ts = chunk_r
            tss, tse = ts
            if isinstance(chunk, list):
                chunk = chunk[0]
            if len(chunk.shape) > 1:
                chunk = chunk.T  # Swap axes if the audio is stereo.
            soundfile.write(
                f"{export_pth}{sp}{fn.split(sp)[-1].split('.')[0] + f'_{tss}_{tse}_{i}'}.wav",
                chunk,
                sr)  # Save sliced audio files with soundfile.
            # print("Successfully exported:", f"clips\\{fn.split(sp)[-1].split('.')[0]}\\{fn.split(sp)[-1].split(
            # '.')[0] + f'_{tss}_{tse}_{i}'}.wav", sr)
    except FileExistsError as err:
        print("ERROR=>", fn, str(err))
    return export_pth


if __name__ == '__main__':
    while True:
        fn = input("Path:").replace('"', "")
        if fn.startswith("DIR"):
            fn = fn[3:]
            for root, dirs, files in os.walk(fn):
                for file in files:
                    if not os.path.isfile(os.path.join(root, file)):
                        continue
                    process(os.path.join(root, file), export_pth=fn.split(os.path.sep)[-1])
        else:
            process(fn)

# MiniMax H3 (video) on Google Colab

[日本語版はこちら（README_ja.md）](README_ja.md)

The notebook and files used in the YouTube video by **AI is in Wonderland**: run MiniMax H3 (video) with ComfyUI on a Google Colab GPU (G4 or A100), make lip-synced cuts from a first frame + a voice + a prompt, and save them to Google Drive.

## Files
| file | what it is |
|---|---|
| `colab_minimax_h3_v15.ipynb` | the notebook (cells 0-6, 9). Run the cells one by one from the top. |
| `workflows/h3_t2v_minimal_864x480.json` | small test: text only, 5 s, 864x480, 4 steps |
| `workflows/h3_i2v_lipsync_1536x864.json` | first frame + voice (lip-sync), 1536x864, 4 steps |
| `h3_job_patch.py` | turns a cut folder (start.png, voice.wav, prompt.txt) into a workflow |
| `sample/c01/` | one sample cut (an original character made for this sample) |
| `auto_cell.py` | the all-in-one cell: paste it into one Colab cell and press ▶ once. It sets up, makes every cut, saves each video to Drive and stops the runtime by itself. |

## Use
1. Colab: Runtime → Change runtime type → **G4** (or A100). T4 / L4 do not have enough memory.
2. Run cells 0 → 5 one by one. Copy the URL from cell 5 and paste it into the address bar of a new tab (clicking it is refused).
3. In ComfyUI run `test_t2v_5s` once. Then run cell 6, reload the ComfyUI page (F5), open `sample_c01` and run it.
4. Your own cuts: put `start.png`, `voice.wav`, `prompt.txt` into `MyDrive/AI_Colab/H3/inputs/<your set>/<cut>/` and change `SET` in cell 6.
5. **Always stop the runtime** with the last cell (Colab compute units are used while connected).

## All-in-one cell (`auto_cell.py`)
Once you know the steps above, you can do everything with one cell:
1. Put your cut folders in `MyDrive/AI_Colab/H3/inputs/<your set>/c01, c02, ...` (each with `start.png`, `voice.wav`, `prompt.txt`).
2. Colab: Runtime → Change runtime type → **G4** (or A100).
3. Paste `auto_cell.py` into one cell, change `SET = 'sample'` to your set's folder name, press ▶ and allow Google Drive.
4. It installs ComfyUI and PyTorch, downloads the 4 models, makes every cut one by one and saves each to `MyDrive/AI_Colab/H3/output/<date_time>_auto/`. Progress is written to `_STATUS.txt` there.
5. When everything is done (or after `MAX_MIN` = 90 minutes, or on an error) it **stops the runtime by itself**. If it stopped half-way, run it again: finished cuts are skipped.

## Licence notes (please read before use)
This repository does **not** contain the model weights. The notebook downloads them from Hugging Face, and they stay under their own licences. This is not legal advice: read the licence texts yourself.
- **MiniMax H3** is under the **MiniMax H3 Community License Agreement** (not an open-source licence): https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE
  - The licence covers only the "Applicable Territory": worldwide **excluding the European Union, the United Kingdom, the Republic of Korea and the United States**. Use of the model, its works and its outputs outside that territory is not authorised by the licence.
  - Commercial products or services with more than 20 million US dollars of yearly revenue need a separate written authorisation from MiniMax.
  - The licence has an Acceptable Use Policy and display rules (e.g. showing "MiniMax H3" / "Powered by MiniMax H3" on products and services that use it). Check the full text.
- The model files come from Hugging Face: `Comfy-Org/MiniMax-H3` (repackaged for ComfyUI, licence: MiniMax H3 Community License) and `Kijai/MiniMax-H3-experimental` (int8 versions of the same model). They follow the MiniMax H3 licence.
- **MiniMax H3-Image** is a different model with a different licence. It is not used here.
- **ComfyUI** is licensed under GPL-3.0: https://github.com/Comfy-Org/ComfyUI
- `sample/c01/` uses an original character made for this sample. Use it only to try the notebook.
- When you publish videos made with H3, we recommend saying that they contain AI-generated video made with MiniMax H3.

## Notes
- H3 **video** only.
- Models are downloaded from Hugging Face (Kijai/MiniMax-H3-experimental, Comfy-Org/MiniMax-H3).
- Do not share the trycloudflare URL.

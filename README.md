# MiniMax H3 (video) on Google Colab

The notebook and files used in the YouTube video by **AI is in Wonderland**: run MiniMax H3 (video) with ComfyUI on a Google Colab GPU (G4 or A100), make lip-synced cuts from a first frame + a voice + a prompt, and save them to Google Drive.

## Files
| file | what it is |
|---|---|
| `colab_minimax_h3_v14.ipynb` | the notebook (cells 0-6, 9). Run the cells one by one from the top. |
| `workflows/h3_t2v_minimal_864x480.json` | small test: text only, 5 s, 864x480, 4 steps |
| `workflows/h3_i2v_lipsync_1536x864.json` | first frame + voice (lip-sync), 1536x864, 4 steps |
| `h3_job_patch.py` | turns a cut folder (start.png, voice.wav, prompt.txt) into a workflow |
| `sample/c01/` | one sample cut (an original character made for this sample) |

## Use
1. Colab: Runtime → Change runtime type → **G4** (or A100). T4 / L4 do not have enough memory.
2. Run cells 0 → 5 one by one. Copy the URL from cell 5 and paste it into the address bar of a new tab (clicking it is refused).
3. In ComfyUI run `test_t2v_5s` once. Then run cell 6, reload the ComfyUI page (F5), open `sample_c01` and run it.
4. Your own cuts: put `start.png`, `voice.wav`, `prompt.txt` into `MyDrive/AI_Colab/H3/inputs/<your set>/<cut>/` and change `SET` in cell 6.
5. **Always stop the runtime** with the last cell (Colab compute units are used while connected).

## Notes
- H3 **video** only. Check the MiniMax H3 licence terms yourself before you use it.
- Models are downloaded from Hugging Face (Kijai/MiniMax-H3-experimental, Comfy-Org/MiniMax-H3).
- Do not share the trycloudflare URL.

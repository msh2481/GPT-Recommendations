# cogtrain
A command-line tool for creativity training. 

## Usage
Create a directory `data` and `extra_questions.jsonl` in it. Each line there is a question that will be tracked for each testing session (e.g. "Your mood on 1 to 5 scale").

Then prepare the tasks you need, e.g. for Insight task:
```bash
python cogtrain.py prepare IS --n 100
```

Finally, run the test:
```bash
python cogtrain.py test IS --n 4 --t 180
```

## Supported tasks

Creativity:

1. Insight (IS): An unusual sitiation is described and the participant is asked to think of different causes for the situation.
2. Utopian situations  (US): The participant is instructed to imagine himself in a utopian situation and identify original consequences.
3. Product improvement (PI): The participant is prompted to think about how to improve a product, e.g. toy elephant, to make it more popular and interesting.
4. Alternative uses (AU): Generating novel uses for common objects.
5. Remote associates test (RAT): The participant is presented with three seemingly unrelated words and must find a fourth word that connects them all. This task measures associative thinking and the ability to make novel connections.

External, just tracking the results:

6. [Codeforces (CF)](https://codeforces.com/): Algorithmic problems. Results are described by problem rating and the time spent to solve it.

## TODO
- Use {"prompt": ..., "answer": ...} format to task instances, rewrite grading
- Track what samples were already used
- Make a shuffle script which removes used samples and shuffles the rest

## References
- Sun, Jiangzhou, et al. "Training your brain to be more creative: brain functional and structural changes induced by divergent thinking training." Human brain mapping 37.10 (2016): 3375-3387
- Olteţeanu, Ana-Maria, Mikkel Schöttner, and Susanne Schuberth. "Computationally resurrecting the functional remote associates test using cognitive word associates and principles from a computational solver." Knowledge-Based Systems 168 (2019): 1-9.
- [XML version of the University of South Florida Free Association Norms (USF-FAN)](http://rali.iro.umontreal.ca/rali/?q=en/USF-FAN)
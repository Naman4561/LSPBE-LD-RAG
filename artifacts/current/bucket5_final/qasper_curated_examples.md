# QASPER Curated Examples

## Flat Clearly Succeeds

- paper_id: `1602.03483`
- question_id: `1602.03483::q3`
- question: Which unsupervised representation-learning objectives do they introduce?
- subset_labels: `skip_local | multi_span | question_type::which`
- final_method_retrieval_hit: `True`
- final_method_prediction: Sequential Denoising Autoencoders ( SDAEs ) and FastSent
- baseline_prediction: predicting adjacent words
- gold_answers: Sequential Denoising Autoencoders (SDAEs) and FastSent || FastSent and Sequential Denoising Autoencoders

## Both Methods Struggle

- paper_id: `1601.03313`
- question_id: `1601.03313::q1`
- question: how was quality of sentence transition measured?
- subset_labels: `skip_local | multi_span | float_table | question_type::how`
- final_method_retrieval_hit: `True`
- final_method_prediction: very good
- baseline_prediction: <empty>
- gold_answers: Manually, using the criterion score between 0 and 3. || The quality of sentence transition was measured manually by checking how well do consecutive sentences connect || Manually evaluated on scale 0 to 3.

## Float Or Table Case

- paper_id: `1601.03313`
- question_id: `1601.03313::q2`
- question: what is the size of the dataset?
- subset_labels: `float_table | question_type::what`
- final_method_retrieval_hit: `True`
- final_method_prediction: <empty>
- baseline_prediction: <empty>
- gold_answers: 3857 speech segments || 2771 speeches containing 50871 sentences || 3857 speech segments from 53 US Congressional floor debates

## Multi-Span Or Nonlocal Case

- paper_id: `1601.03313`
- question_id: `1601.03313::q3`
- question: what manual evaluation is presented?
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- final_method_retrieval_hit: `True`
- final_method_prediction: a generated speech
- baseline_prediction: <empty>
- gold_answers: Manual evaluation of four evaluation criteria:   grammatical correctness,  sentence transitions, speech structure, and speech content. || generated speech is evaluated by assessing each of the criterion and assigning a score between 0 and 3 to it || The manual evaluation contains 4 criteria to check grammatical correctness, sentence transitions, speech structure, and speech content of the generated speech and assigning a score between 0 to 3 for each criterion

## Answerer Mismatch Limitation

- paper_id: `1602.03483`
- question_id: `1602.03483::q0`
- question: Which data sources do they use?
- subset_labels: `skip_local | multi_span | float_table | question_type::which`
- final_method_retrieval_hit: `True`
- final_method_prediction: BOW and RNN
- baseline_prediction: dense real - valued vectors
- gold_answers: Toronto Books Corpus || STS 2014 dataset BIBREF37 || SICK dataset BIBREF36 || SICK || STS 2014

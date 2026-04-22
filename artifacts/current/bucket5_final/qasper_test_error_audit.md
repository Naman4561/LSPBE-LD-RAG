# QASPER Test Error Audit

- audited_examples: `50`
- note: this is a compact presentation-oriented audit, not a full relabeling pass.

## 1603.07252::q0

- paper_id: `1603.07252`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: What domain of text are they working with?
- predicted_answer: Multiple Modalities into Text
- gold_answers: news articles || news
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1909.09070::q1

- paper_id: `1909.09070`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: What language are the captions in?
- predicted_answer: natural
- gold_answers: English
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1908.07721::q0

- paper_id: `1908.07721`
- subset_labels: `skip_local | multi_span | float_table | question_type::how`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: How do they perform the joint training?
- predicted_answer: through a specially designed tagging scheme
- gold_answers: They train a single model that integrates a BERT language model as a shared parameter layer on NER and RC tasks. || They perform joint learning through shared parameters for NER and RC.
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1909.13466::q0

- paper_id: `1909.13466`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: What baselines do they compare to?
- predicted_answer: LSTM and transformer
- gold_answers: a encoder-decoder architecture with attention incorporating LSTMs and transformers || A neural encoder-decoder architecture with attention using LSTMs or Transformers
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1908.05758::q1

- paper_id: `1908.05758`
- subset_labels: `skip_local | multi_span | question_type::boolean`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: Does the SESAME dataset include discontiguous entities?
- predicted_answer: yes
- gold_answers: no
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1602.07776::q0

- paper_id: `1602.07776`
- subset_labels: `float_table | question_type::what`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: what state of the art models do they compare to?
- predicted_answer: <empty>
- gold_answers: Vinyals et al (2015) for English parsing, Wang et al (2015) for Chinese parsing, and LSTM LM for Language modeling both in English and Chinese || IKN 5-gram, LSTM LM
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1603.00957::q3

- paper_id: `1603.00957`
- subset_labels: `float_table | question_type::how`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: How much improvement they get from the previous state-of-the-art?
- predicted_answer: 6. 2 %
- gold_answers: 0.8 point improvement || 0.8 point on average (question-wise) F1 measure
- note: No gold evidence reached the final context; seed first-rank=miss.

## 1605.04278::q1

- paper_id: `1605.04278`
- subset_labels: `float_table | question_type::what`
- retrieval_hit: `False`
- evidence_coverage: `0.0000`
- category: `wrong seed / retrieval miss`
- question: What are their baseline models?
- predicted_answer: <empty>
- gold_answers: version 2.2 of the Turbo tagger and Turbo parser BIBREF18 || Turbo tagger || Turbo parser
- note: No gold evidence reached the final context; seed first-rank=miss.

## 2004.02214::q1

- paper_id: `2004.02214`
- subset_labels: `skip_local | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.2667`
- category: `partial evidence recovery`
- question: What are existing baseline models on these benchmark datasets?
- predicted_answer: individual styles as well as the overall results
- gold_answers: Seq2seq || GPT2-FT || Speaker || ECM || Skeleton-to-Response (SR) || Retrieval + Style Transfer (RST) || Retrieval + Reranking (RRe) || Generative Approaches ::: Seq2seq || Generative Approaches ::: GPT2-FT: || Generative Approaches ::: Speaker: || Generative Approaches ::: ECM: || Retrieval-Based Approaches ::: Skeleton-to-Response (SR) || Retrieval-Based Approaches ::: Retrieval + Style Transfer (RST) || Retrieval-Based Approaches ::: Retrieval + Reranking (RRe)
- note: Retrieval hit succeeded but coverage stayed at 0.27, leaving part of the gold evidence unrecovered.

## 2003.07568::q2

- paper_id: `2003.07568`
- subset_labels: `skip_local | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.2500`
- category: `partial evidence recovery`
- question: Which translation pipelines do they use to compare against?
- predicted_answer: cross - lingual and multilingual
- gold_answers: Translate source sentence to English with Google Translate API and then translate the result to the target language with Poly-encoder. || M-Bert2Bert || M-CausalBert || Bert2Bert || CausalBert || Poly-encoder BIBREF75 || XNLG || Google Translate API
- note: Retrieval hit succeeded but coverage stayed at 0.25, leaving part of the gold evidence unrecovered.

## 1707.06875::q0

- paper_id: `1707.06875`
- subset_labels: `skip_local | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.4000`
- category: `partial evidence recovery`
- question: Which metrics were considered?
- predicted_answer: WBMs
- gold_answers: ter || bleu || rouge || nist || lepor || cider || meteor || Semantic Text Similarity || Flesch Reading Ease || characters per utterance (len) and per word (cpw) || words per sentence || syllables per sentence (sps) and per word (spw) || polysyllabic words per utterance (pol) and per word (ppw) || the number of misspellings (msp) and the parsing score as returned by the Stanford parser (prs) || Semantic Similarity (sim) || readability and grammaticality || ter BIBREF18 , bleu BIBREF0 , rouge BIBREF19 , nist BIBREF20 , lepor BIBREF21 , cider BIBREF22 , and meteor BIBREF23
- note: Retrieval hit succeeded but coverage stayed at 0.40, leaving part of the gold evidence unrecovered.

## 1709.06365::q3

- paper_id: `1709.06365`
- subset_labels: `skip_local | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.3333`
- category: `partial evidence recovery`
- question: Which data augmentation techniques do they use?
- predicted_answer: the posterior is transformed into a form that is conjugate to the gamma prior of INLINEFORM9
- gold_answers: augmented with a set of Beta random variables || auxiliary variable || the introduction of auxiliary variables
- note: Retrieval hit succeeded but coverage stayed at 0.33, leaving part of the gold evidence unrecovered.

## 1709.06365::q0

- paper_id: `1709.06365`
- subset_labels: `skip_local | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.5000`
- category: `partial evidence recovery`
- question: Which real world datasets do they experiment on?
- predicted_answer: 6 real datasets including both regular and short texts
- gold_answers: Reuters || 20 Newsgroup || New York Times || Web Snippet || Tag My News || ABC News || 20NG, 20 Newsgroup || NYT, New York Times || WS, Web Snippet || TMN, Tag My News || Reuters-21578 dataset
- note: Retrieval hit succeeded but coverage stayed at 0.50, leaving part of the gold evidence unrecovered.

## 1909.07158::q0

- paper_id: `1909.07158`
- subset_labels: `skip_local | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.5000`
- category: `partial evidence recovery`
- question: what dataset were used?
- predicted_answer: Section SECREF5
- gold_answers: HatEval || YouToxic || OffensiveTweets
- note: Retrieval hit succeeded but coverage stayed at 0.50, leaving part of the gold evidence unrecovered.

## 2004.04498::q2

- paper_id: `2004.04498`
- subset_labels: `skip_local | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.5714`
- category: `partial evidence recovery`
- question: What metrics are used to measure bias reduction?
- predicted_answer: <empty>
- gold_answers: Accuracy || $\mathbf {\Delta G}$ || $\mathbf {\Delta S}$ || BLEU || $\mathbf {\Delta G}$ – difference in $F_1$ score between the set of sentences with masculine entities and the set with feminine entities || $\mathbf {\Delta S}$ – difference in accuracy between the set of sentences with pro-stereotypical (`pro') entities and those with anti-stereotypical (`anti') entities
- note: Retrieval hit succeeded but coverage stayed at 0.57, leaving part of the gold evidence unrecovered.

## 2003.07568::q0

- paper_id: `2003.07568`
- subset_labels: `skip_local | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.6667`
- category: `partial evidence recovery`
- question: What kind of evaluations do use to evaluate dialogue?
- predicted_answer: A / B test
- gold_answers: They use automatic evaluation using perplexity and BLEU scores with reference to the human-annotated responses and human evaluation on interestingness, engagingness, and humanness. || perplexity (ppl.) and BLEU || which of the two dialogues is better in terms of engagingness, interestingness, and humanness || perplexity || BLEU || ACUTE-EVA
- note: Retrieval hit succeeded but coverage stayed at 0.67, leaving part of the gold evidence unrecovered.

## 2003.04978::q1

- paper_id: `2003.04978`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.0435`
- category: `multi-span miss`
- question: What models are explored in this paper?
- predicted_answer: <empty>
- gold_answers: SVM, Logistic Regression, ANN, LSTM, and Random Forest || Artificial Neural Network (ANN) || Long Short Term Memory networks (LSTMs) || Random Forest || Logistic Regression || Support Vector Machine (SVM) || SVM || ANN || LSTM || TFIDF || CV || W2V
- note: Multi-span question with retrieval hit=True but coverage 0.04, so at least one needed span stayed out.

## 1909.07873::q5

- paper_id: `1909.07873`
- subset_labels: `skip_local | multi_span | question_type::boolean`
- retrieval_hit: `True`
- evidence_coverage: `0.2000`
- category: `multi-span miss`
- question: Do they use already trained model on some task in their reinforcement learning approach?
- predicted_answer: no
- gold_answers: yes
- note: Multi-span question with retrieval hit=True but coverage 0.20, so at least one needed span stayed out.

## 1912.07076::q1

- paper_id: `1912.07076`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.2000`
- category: `multi-span miss`
- question: What previous proposed methods did they explore?
- predicted_answer: ability of the models to capture linguistic properties using the probing tasks
- gold_answers: ELMo || ULMFit || BERT || che2018towards || lim2018sex || FiNER-tagger BIBREF32 || gungor2018 || HIT-SCIR BIBREF22 || BIBREF33
- note: Multi-span question with retrieval hit=True but coverage 0.20, so at least one needed span stayed out.

## 2003.09244::q2

- paper_id: `2003.09244`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.3750`
- category: `multi-span miss`
- question: What concrete software is planned to be developed by the end of the programme?
- predicted_answer: <empty>
- gold_answers: A lot of new software will be developed in all areas of the programme, some will be extensions of already available Greynir software. || IceNLP || Greynir || Nefnir || ABLTagger || a flexible lexicon acquisition tool || A punctuation system for Icelandic || open source correction system || a statistical phrase-based MT system || a bidirectional LSTM model using the neural translation system OpenNMT || a system based on an attention-based neural network || An API and a web user interface
- note: Multi-span question with retrieval hit=True but coverage 0.38, so at least one needed span stayed out.

## 1602.07563::q2

- paper_id: `1602.07563`
- subset_labels: `skip_local | multi_span | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.4000`
- category: `multi-span miss`
- question: Which measures of inter-annotator agreement are used?
- predicted_answer: inter - rater agreement and machine learning
- gold_answers: Krippendorff's Alpha-reliability || Krippendorff's Alpha-reliability ( INLINEFORM0 ) BIBREF6 || F score ( INLINEFORM0 ) || Accuracy ( INLINEFORM0 ) || Accuracy within 1 ( INLINEFORM0 )
- note: Multi-span question with retrieval hit=True but coverage 0.40, so at least one needed span stayed out.

## 1611.04887::q1

- paper_id: `1611.04887`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.4000`
- category: `multi-span miss`
- question: What conclusions do the authors draw from their experiments?
- predicted_answer: <empty>
- gold_answers: among supervised models, CNN, LSTM and BLSTM encapsulates most of the syntactic and social properties with a great accuracy, while BOW, DSSM, STV and T2V does that among the unsupervised models || Tweet length affects the task prediction accuracies || LDA is insensitive to input word order, CNN, LSTM and BLSTM are extremely sensitive || CNN, LSTM and BLSTM encapsulates most of the syntactic and social properties with a great accuracy, while BOW, DSSM, STV and T2V does that among the unsupervised models || CNN, LSTM and BLSTM are extremely sensitive to word order || Supervised models CNN, LSTM and BLSTM and unsupervised models BOW, DSSM, STV and T2V can  encapsulate most of the syntactic and social properties. Tweet length affects the task prediction accuracies for all models. LDA is insensitive to input word order, but, CNN, LSTM
and BLSTM are not.
- note: Multi-span question with retrieval hit=True but coverage 0.40, so at least one needed span stayed out.

## 1908.11664::q3

- paper_id: `1908.11664`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.4444`
- category: `multi-span miss`
- question: what four learning strategies are investigated?
- predicted_answer: in - domain, out - of - domain and cross - dataset
- gold_answers: Model@!START@$^{I}_{Base}$@!END@ || $Model^{I}_{Base}$ with BERT BIBREF28 || Model@!START@$^{III}_{Tag}$@!END@ || Model@!START@$^{IV}_{Meta}$@!END@ || Model@!START@$^{II}_{BERT}$@!END@
- note: Multi-span question with retrieval hit=True but coverage 0.44, so at least one needed span stayed out.

## 1906.01615::q0

- paper_id: `1906.01615`
- subset_labels: `skip_local | multi_span | question_type::how`
- retrieval_hit: `True`
- evidence_coverage: `0.3333`
- category: `multi-span miss`
- question: How do attention, recurrent and convolutional networks differ on the language classes they accept?
- predicted_answer: complete automata - theoretic characterization of sequential neural networks
- gold_answers: Attention neural networks can represent more languages than other networks. Simple recurring networks can describe regular languages. CNNs can describe only strictly local languages.
- note: Multi-span question with retrieval hit=True but coverage 0.33, so at least one needed span stayed out.

## 1603.01547::q2

- paper_id: `1603.01547`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.1111`
- category: `float/table-related miss`
- question: What baseline do they compare against?
- predicted_answer: all candidate answers INLINEFORM8
- gold_answers: Attentive and Impatient Readers || Chen et al. 2016 || MenNN || Dynamic Entity Representation || LSTM
- note: Figure/table-linked case with coverage 0.11; predicted answer was all candidate answers INLINEFORM8.

## 1612.00866::q0

- paper_id: `1612.00866`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.1667`
- category: `float/table-related miss`
- question: What new advances are included in this dataset?
- predicted_answer: <empty>
- gold_answers: PETRARCH || PETRARCH2 || realtime event data || geolocation || scraping of news content from the web || geolocation of the coded events || a comprehensive pipeline
- note: Figure/table-linked case with coverage 0.17; predicted answer was <empty>.

## 1911.01214::q5

- paper_id: `1911.01214`
- subset_labels: `skip_local | multi_span | float_table | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.1667`
- category: `float/table-related miss`
- question: which architectures did they experiment with?
- predicted_answer: FEVER corpus
- gold_answers: For stance detection they used MLP, for evidence extraction they used Tf-idf and BiLSTM, for claim validation they used MLP, BiLSTM and SVM || AtheneMLP || DecompAttent BIBREF20 || USE+Attent
- note: Figure/table-linked case with coverage 0.17; predicted answer was FEVER corpus.

## 1909.12079::q1

- paper_id: `1909.12079`
- subset_labels: `skip_local | multi_span | float_table | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `0.2500`
- category: `float/table-related miss`
- question: Which model architecture do they use?
- predicted_answer: FIGER
- gold_answers: BiLSTMs || MLP || BiLSTM with a three-layer perceptron || BiLSTM
- note: Figure/table-linked case with coverage 0.25; predicted answer was FIGER.

## 1811.04791::q1

- paper_id: `1811.04791`
- subset_labels: `skip_local | multi_span | float_table | question_type::how`
- retrieval_hit: `True`
- evidence_coverage: `0.3333`
- category: `float/table-related miss`
- question: How do they extract target language bottleneck features?
- predicted_answer: multilingual annotated data
- gold_answers: train a tdnn BIBREF36 with block softmax || tdnn has six 625-dimensional hidden layers followed by a 39-dimensional bottleneck layer || Extracting cae features requires three steps, as illustrated in Figure FIGREF6 . First, an utd system is applied to the target language to extract pairs of speech segments that are likely to be instances of the same word or phrase
- note: Figure/table-linked case with coverage 0.33; predicted answer was multilingual annotated data.

## 1909.12208::q2

- paper_id: `1909.12208`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.3333`
- category: `float/table-related miss`
- question: What was previous single-system state of the art result on the CHiME-5 data?
- predicted_answer: 45. 1 % and 47. 3 %
- gold_answers: BIBREF12 (H/UPB) || Previous single system state of the art had WER of  58.3 (53.1).
- note: Figure/table-linked case with coverage 0.33; predicted answer was 45. 1 % and 47. 3 %.

## 2002.10210::q3

- paper_id: `2002.10210`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.3333`
- category: `float/table-related miss`
- question: What is the size of built dataset?
- predicted_answer: <empty>
- gold_answers: Document-level dataset has total of 4821 instances. 
Sentence-level dataset has total of 45583 instances. || Total number of documents is 4821. Total number of sentences is 47583.
- note: Figure/table-linked case with coverage 0.33; predicted answer was <empty>.

## 2004.04478::q3

- paper_id: `2004.04478`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.3333`
- category: `float/table-related miss`
- question: What 20 domains are available for selection of source domain?
- predicted_answer: CDSA
- gold_answers: Amazon Instant Video,  Automotive, Baby,  Beauty, Books,  Clothing Accessories,  Electronics,  Health, Home, Kitchen, Movies, Music,  Office Products, Patio, Pet Supplies, Shoes,  Software,  Sports Outdoors,  Tools Home Improvement, Toys Games, Video Games. || Amazon Instant Video
Automotive
Baby
Beauty
Books
Clothing Accessories
Electronics
Health
Home Kitchen
Movies TV
Music
Office Products
Patio
Pet Supplies
Shoes
Software
Sports Outdoors
Tools Home Improvement
Toys Games
Video Games
- note: Figure/table-linked case with coverage 0.33; predicted answer was CDSA.

## 1810.12897::q2

- paper_id: `1810.12897`
- subset_labels: `skip_local | multi_span | float_table | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: Which widely used dataset did the authors use?
- predicted_answer: BIBREF3
- gold_answers: Convote dataset BIBREF3
- note: Correct evidence was present, but answer matching stayed soft (F1 0.50) against multiple or free-form golds.

## 1908.11053::q2

- paper_id: `1908.11053`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: What knowledge base do they rely on?
- predicted_answer: DBpedia and Freebase
- gold_answers: DBpedia (2016-04) || DBpedia (2015-10) || DBpedia
- note: Correct evidence was present, but answer matching stayed soft (F1 0.50) against multiple or free-form golds.

## 1610.03807::q1

- paper_id: `1610.03807`
- subset_labels: `skip_local | multi_span | float_table | question_type::how`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: How was domain relevance estimated?
- predicted_answer: we take the seed question set as the in - domain data $ D _ { in } $
- gold_answers: For domain relevance, we take the seed question set as the in-domain data $D_{in}$ , the domain relevance of expanded question $q$ is defined as:

$$\textsc {Rel}(q) = \cos (v(q),v(D_{in}))$$ (Eq. 7)

where $v(\cdot )$ is the document embedding defined as the averaged word embedding within the document. || the domain relevance of expanded question $q$ is defined as:

$$\textsc {Rel}(q) = \cos (v(q),v(D_{in}))$$ (Eq. 7)

where $v(\cdot )$ is the document embedding defined as the averaged word embedding within the document || we take the seed question set as the in-domain data $D_{in}$ , the domain relevance of expanded question $q$ is defined as:

$$\textsc {Rel}(q) = \cos (v(q),v(D_{in}))$$
- note: Correct evidence was present, but answer matching stayed soft (F1 0.55) against multiple or free-form golds.

## 1906.01502::q4

- paper_id: `1906.01502`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: What datasets did they use?
- predicted_answer: CoNLL - 2002 and - 2003 sets, containing Dutch, Spanish, English, and German BIBREF5, BIBREF6
- gold_answers: CoNLL-2002 and -2003 || Universal Dependencies || WMT16 || CoNLL-2002 and -2003 sets || an in-house dataset with 16 languages || Universal Dependencies (UD) BIBREF7
- note: Correct evidence was present, but answer matching stayed soft (F1 0.56) against multiple or free-form golds.

## 1805.04558::q1

- paper_id: `1805.04558`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: what was the size of the datasets?
- predicted_answer: 8, 000 tweets and a development set containing 2, 260 tweets
- gold_answers: 10822, 4845 || training set containing 10,822 tweets and a development set containing 4,845 tweets || test set of 9,961 tweets was provided without labels || training set containing 8,000 tweets and a development set containing 2,260 tweets || test set of 7,513 tweets
- note: Correct evidence was present, but answer matching stayed soft (F1 0.57) against multiple or free-form golds.

## 1708.09025::q2

- paper_id: `1708.09025`
- subset_labels: `skip_local | multi_span | float_table | question_type::how`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: How do they measure the usefulness of obtained ontologies compared to domain expert ones?
- predicted_answer: precision, recall and F - measure
- gold_answers: precision || recall || F-measure || We use KB-LDA, phrase_hLDA, and LDA+GSHL as our baseline methods, and compare ontologies extracted from hrLDA, KB-LDA, phrase_hLDA, and LDA+GSHL with DBpedia ontologies. We use precision, recall and F-measure for this ontology evaluation. A true positive case is an ontology rule that can be found in an extracted ontology and the associated ontology of DBpedia. A false positive case is an incorrectly identified ontology rule. A false negative case is a missed ontology rule.
- note: Correct evidence was present, but answer matching stayed soft (F1 0.57) against multiple or free-form golds.

## 1910.01160::q2

- paper_id: `1910.01160`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: What is the baseline?
- predicted_answer: Multinomial Naive Bayes from BIBREF1
- gold_answers: Naive Bayes Multinomial algorithm || model using the Naive Bayes Multinomial algorithm
- note: Correct evidence was present, but answer matching stayed soft (F1 0.67) against multiple or free-form golds.

## 1905.07562::q1

- paper_id: `1905.07562`
- subset_labels: `skip_local | multi_span | float_table | question_type::how`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `annotation ambiguity / evaluation ambiguity`
- question: How do the authors measure the extent to which LGI has learned the task?
- predicted_answer: high precision
- gold_answers: precision || accuracy || classify figures in various morphology with correct identity (accuracy = 72.7%) || demonstrates that LGI can understand the verbs and nouns
- note: Correct evidence was present, but answer matching stayed soft (F1 0.67) against multiple or free-form golds.

## 1605.05195::q2

- paper_id: `1605.05195`
- subset_labels: `skip_local | multi_span | question_type::boolean`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: Are there any other standard linguistic features used, other than ngrams?
- predicted_answer: yes
- gold_answers: no
- note: Correct evidence was present but the answerer still produced yes (token F1 0.00).

## 1710.11334::q1

- paper_id: `1710.11334`
- subset_labels: `skip_local | multi_span | question_type::boolean`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: Do they try to use other models aside from Maximum Entropy?
- predicted_answer: yes
- gold_answers: no
- note: Correct evidence was present but the answerer still produced yes (token F1 0.00).

## 1809.03391::q3

- paper_id: `1809.03391`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: what datasets have been used for this task?
- predicted_answer: 10K sentences and 250K tokens
- gold_answers: IDN Tagged Corpus
- note: Correct evidence was present but the answerer still produced 10K sentences and 250K tokens (token F1 0.00).

## 1905.08067::q0

- paper_id: `1905.08067`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: What languages feature in the dataset?
- predicted_answer: known - bad and random - good
- gold_answers: English
- note: Correct evidence was present but the answerer still produced known - bad and random - good (token F1 0.00).

## 1912.08084::q3

- paper_id: `1912.08084`
- subset_labels: `skip_local | multi_span | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: What is the strong rivaling system?
- predicted_answer: by a margin
- gold_answers: ClaimBuster
- note: Correct evidence was present but the answerer still produced by a margin (token F1 0.00).

## 1910.10487::q2

- paper_id: `1910.10487`
- subset_labels: `skip_local | float_table | question_type::which`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: Which of two design architectures have better performance?
- predicted_answer: NTM - LM architecture
- gold_answers: NTM-LM
- note: Correct evidence was present but the answerer still produced NTM - LM architecture (token F1 0.80).

## 1901.10619::q1

- paper_id: `1901.10619`
- subset_labels: `skip_local | question_type::other`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: The authors point out a relevant constraint on the previous corpora of workplace, do they authors mention any relevant constrains on this corpus?
- predicted_answer: <empty>
- gold_answers: no
- note: Correct evidence was present but the answerer still produced <empty> (token F1 0.00).

## 2002.08902::q1

- paper_id: `2002.08902`
- subset_labels: `float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `1.0000`
- category: `answerer failure despite correct evidence`
- question: what was the baseline?
- predicted_answer: BiGRU + CRF model
- gold_answers: BiGRU+CRF
- note: Correct evidence was present but the answerer still produced BiGRU + CRF model (token F1 0.80).

## 1908.09590::q2

- paper_id: `1908.09590`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.1667`
- category: `float/table-related miss`
- question: What are the performances associated to different attribute placing?
- predicted_answer: ( 1 ) the bias - attention method, and ( 2 - 5 ) the CHIM - based representation method injected to all four different locations in the model
- gold_answers: Best accuracy is for proposed CHIM methods (~56% IMDB, ~68.5 YELP datasets), most common bias attention (~53%IMDB, ~65%YELP), and oll others are worse than proposed method. || Sentiment classification (datasets IMDB, Yelp 2013, Yelp 2014): 
embedding 56.4% accuracy, 1.161 RMSE, 67.8% accuracy, 0.646 RMSE, 69.2% accuracy, 0.629 RMSE;
encoder 55.9% accuracy, 1.234 RMSE, 67.0% accuracy, 0.659 RMSE, 68.4% accuracy, 0.631 RMSE;
attention 54.4% accuracy, 1.219 RMSE, 66.5% accuracy, 0.664 RMSE, 68.5% accuracy, 0.634 RMSE;
classifier 55.5% accuracy, 1.219 RMSE, 67.5% accuracy, 0.641 RMSE, 68.9% accuracy, 0.622 RMSE.

Product category classification and review headline generation:
embedding 62.26 ± 0.22% accuracy, 42.71 perplexity;
encoder 64.62 ± 0.34% accuracy, 42.65 perplexity;
attention 60.95 ± 0.15% accuracy, 42.78 perplexity;
classifier 61.83 ± 0.43% accuracy, 42.69 perplexity.
- note: Figure/table-linked case with coverage 0.17; predicted answer was ( 1 ) the bias - attention method, and ( 2 - 5 ) the CHIM - based representation method injected to all four different locations in the model.

## 1805.04558::q3

- paper_id: `1805.04558`
- subset_labels: `skip_local | multi_span | float_table | question_type::what`
- retrieval_hit: `True`
- evidence_coverage: `0.2500`
- category: `float/table-related miss`
- question: what were their results on both tasks?
- predicted_answer: share the same classification framework and feature pool
- gold_answers: 0.435 on Task1 and 0.673 on Task2.
- note: Figure/table-linked case with coverage 0.25; predicted answer was share the same classification framework and feature pool.

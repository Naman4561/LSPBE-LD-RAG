# MVE Debug Examples

These examples show the cleaned gold evidence and the retrieved context for each method.
The goal is qualitative inspection, so segments are listed with section names and ids.

## Example 1

- paper_id: `1909.00694`
- question: What is the seed lexicon?
- gold evidence:
  - The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- note: Bridge seems to do about the same here based on the current evidence-hit proxy.

### Flat
- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: AL (Automatically Labeled Pairs)`
- segment_id: `6`
- text: The seed lexicon matches (1) the latter event but (2) not the former event, and (3) their discourse relation type is Cause or Concession. If the discourse relation type is Cause, the former event is given the same score as the latter. Likewise, if the discourse relation type is Concession, the former event is given the opposite of the latter's score. They are used as reference scores during training.

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.

### Adjacency
- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: AL (Automatically Labeled Pairs)`
- segment_id: `6`
- text: The seed lexicon matches (1) the latter event but (2) not the former event, and (3) their discourse relation type is Cause or Concession. If the discourse relation type is Cause, the former event is given the same score as the latter. Likewise, if the discourse relation type is Concession, the former event is given the opposite of the latter's score. They are used as reference scores during training.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.

- section: `Proposed Method ::: Loss Functions`
- segment_id: `9`
- text: Using AL, CA, and CO data, we optimize the parameters of the polarity function $p(x)$. We define a loss function for each of the three types of event pairs and sum up the multiple loss functions. We use mean squared error to construct loss functions. For the AL data, the loss function is defined as: where $x_{i1}$ and $x_{i2}$ are the $i$-th pair of the AL data. $r_{i1}$ and $r_{i2}$ are the automatically-assigned scores of $x_{i1}$ and $x_{i2}$, respectively. $N_{\rm AL}$ is the total number of AL pairs, and $\lambda _{\rm AL}$ is a hyperparameter. For the CA data, the loss function is defined as: $y_{i1}$ and $y_{i2}$ are the $i$-th pair of the CA pairs. $N_{\rm CA}$ is the total number of CA pairs. $\lambda _{\rm CA}$ and $\mu $ are hyperparameters. The first term makes the scores of the two events closer while the second term prevents the scores from shrinking to zero. The loss function for the CO data is defined analogously: The difference is that the first term makes the scores of the two events distant from each other.

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `10`
- text: As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction. . 重大な失敗を犯したので、仕事をクビになった。 Because [I] made a serious mistake, [I] got fired.

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:

### Bridge
- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.
- bridge_detail: seed=`5`, total=`1.111`, adjacency=`1.000`, entity_overlap=`0.111`, section_continuity=`0.000`

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- bridge_detail: seed=`6`, total=`1.375`, adjacency=`1.000`, entity_overlap=`0.375`, section_continuity=`0.000`

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: AL (Automatically Labeled Pairs)`
- segment_id: `6`
- text: The seed lexicon matches (1) the latter event but (2) not the former event, and (3) their discourse relation type is Cause or Concession. If the discourse relation type is Cause, the former event is given the same score as the latter. Likewise, if the discourse relation type is Concession, the former event is given the opposite of the latter's score. They are used as reference scores during training.
- bridge_detail: seed=`7`, total=`1.400`, adjacency=`1.000`, entity_overlap=`0.400`, section_continuity=`0.000`

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.
- bridge_detail: seed=`6`, total=`1.400`, adjacency=`1.000`, entity_overlap=`0.400`, section_continuity=`0.000`

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.
- bridge_detail: seed=`7`, total=`1.333`, adjacency=`1.000`, entity_overlap=`0.333`, section_continuity=`0.000`

- section: `Proposed Method ::: Loss Functions`
- segment_id: `9`
- text: Using AL, CA, and CO data, we optimize the parameters of the polarity function $p(x)$. We define a loss function for each of the three types of event pairs and sum up the multiple loss functions. We use mean squared error to construct loss functions. For the AL data, the loss function is defined as: where $x_{i1}$ and $x_{i2}$ are the $i$-th pair of the AL data. $r_{i1}$ and $r_{i2}$ are the automatically-assigned scores of $x_{i1}$ and $x_{i2}$, respectively. $N_{\rm AL}$ is the total number of AL pairs, and $\lambda _{\rm AL}$ is a hyperparameter. For the CA data, the loss function is defined as: $y_{i1}$ and $y_{i2}$ are the $i$-th pair of the CA pairs. $N_{\rm CA}$ is the total number of CA pairs. $\lambda _{\rm CA}$ and $\mu $ are hyperparameters. The first term makes the scores of the two events closer while the second term prevents the scores from shrinking to zero. The loss function for the CO data is defined analogously: The difference is that the first term makes the scores of the two events distant from each other.
- bridge_detail: seed=`8`, total=`1.250`, adjacency=`1.000`, entity_overlap=`0.250`, section_continuity=`0.000`

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `10`
- text: As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction. . 重大な失敗を犯したので、仕事をクビになった。 Because [I] made a serious mistake, [I] got fired.
- bridge_detail: seed=`11`, total=`2.062`, adjacency=`1.000`, entity_overlap=`0.062`, section_continuity=`1.000`

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:
- bridge_detail: seed=`11`, total=`1.071`, adjacency=`1.000`, entity_overlap=`0.071`, section_continuity=`0.000`

## Example 2

- paper_id: `1909.00694`
- question: What are the results?
- gold evidence:
  - FLOAT SELECTED: Table 3: Performance of various models on the ACP test set.
  - FLOAT SELECTED: Table 4: Results for small labeled training data. Given the performance with the full dataset, we show BERT trained only with the AL data.
  - As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states.
  - We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.
- note: Bridge seems to do about the same here based on the current evidence-hit proxy.

### Flat
- section: `Experimental Studies`
- segment_id: `13`
- text: In this section, we devote to experimentally evaluating our proposed task and approach. The best results in tables are in bold.

- section: `Experimental Studies ::: Dataset and Evaluation Metrics`
- segment_id: `14`
- text: Our dataset is annotated based on Chinese pathology reports provided by the Department of Gastrointestinal Surgery, Ruijin Hospital. It contains 17,833 sentences, 826,987 characters and 2,714 question-answer pairs. All question-answer pairs are annotated and reviewed by four clinicians with three types of questions, namely tumor size, proximal resection margin and distal resection margin. These annotated instances have been partitioned into 1,899 training instances (12,412 sentences) and 815 test instances (5,421 sentences). Each instance has one or several sentences. Detailed statistics of different types of entities are listed in Table TABREF20. In the following experiments, two widely-used performance measures (i.e., EM-score BIBREF34 and (macro-averaged) F$_1$-score BIBREF35) are used to evaluate the methods. The Exact Match (EM-score) metric measures the percentage of predictions that match any one of the ground truth answers exactly. The F$_1$-score metric is a looser metric measures the average overlap between the prediction and ground truth answer.

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `40`
- text: \subsection{Comparative user study} \label{sec:comparison} We wanted to evaluate the effectiveness of fake reviews againsttech-savvy users who understand and know to expect machine-generated fake reviews. We conducted a user study with 20 participants, all with computer science education and at least one university degree. Participant demographics are shown in Table~/ref{table:amt_pop} in the Appendix. Each participant first attended a training session where they were asked to label reviews (fake and genuine) and could later compare them to the correct answers -- we call these participants \emph{experienced participants}. No personal data was collected during the user study.

- section: `Acknowledgment`
- segment_id: `23`
- text: We would like to thank Ting Li and Xizhou Hong (Ruijin Hospital) who have helped us very much in data fetching and data cleansing. This work is supported by the National Key R&D Program of China for “Precision Medical Research" (No. 2018YFC0910500).

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `58`
- text: \section*{Acknowledgments} We thank Tommi Gr\"{o}ndahl for assistance in planning user studies and the participants of the user study for their time and feedback. We also thank Luiza Sayfullina for comments that improved the manuscript. We thank the authors of \cite{yao2017automated} for answering questions about their work.

### Adjacency
- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `39`
- text: We can see that our new generated reviews do not share strong attributes with previous known categories of fake reviews. If anything, our fake reviews are more similar to genuine reviews than previous fake reviews. We thus conjecture that our NMT-Fake* fake reviews present a category of fake reviews that may go undetected on online review sites.

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `40`
- text: \subsection{Comparative user study} \label{sec:comparison} We wanted to evaluate the effectiveness of fake reviews againsttech-savvy users who understand and know to expect machine-generated fake reviews. We conducted a user study with 20 participants, all with computer science education and at least one university degree. Participant demographics are shown in Table~/ref{table:amt_pop} in the Appendix. Each participant first attended a training session where they were asked to label reviews (fake and genuine) and could later compare them to the correct answers -- we call these participants \emph{experienced participants}. No personal data was collected during the user study.

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `41`
- text: Each person was given two randomly selected sets of 30 of reviews (a total of 60 reviews per person) with reviews containing 10 \textendash 50 words each. Each set contained 26 (87\%) real reviews from Yelp and 4 (13\%) machine-generated reviews, numbers chosen based on suspicious review prevalence on Yelp~/cite{mukherjee2013yelp,rayana2015collective}. One set contained machine-generated reviews from one of the two models (NMT ($b=0.3, \lambda=-5$) or LSTM), and the other set reviews from the other in randomized order. The number of fake reviews was revealed to each participant in the study description. Each participant was requested to mark four (4) reviews as fake.

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `57`
- text: In this paper, we showed that neural machine translation models can be used to generate fake reviews that are very effective in deceiving even experienced, tech-savvy users. This supports anecdotal evidence \cite{national2017commission}. Our technique is more effective than state-of-the-art \cite{yao2017automated}. We conclude that machine-aided fake review detection is necessary since human users are ineffective in identifying fake reviews. We also showed that detectors trained using one type of fake reviews are not effective in identifying other types of fake reviews. Robust detection of fake reviews is thus still an open problem.

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `58`
- text: \section*{Acknowledgments} We thank Tommi Gr\"{o}ndahl for assistance in planning user studies and the participants of the user study for their time and feedback. We also thank Luiza Sayfullina for comments that improved the manuscript. We thank the authors of \cite{yao2017automated} for answering questions about their work.

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `59`
- text: \bibliographystyle{splncs} \begin{thebibliography}{10} \bibitem{yao2017automated} Yao, Y., Viswanath, B., Cryan, J., Zheng, H., Zhao, B.Y.: \newblock Automated crowdturfing attacks and defenses in online review systems. \newblock In: Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security, ACM (2017)

- section: `The Proposed Model for QA-CTS Task ::: Two-Stage Training Mechanism`
- segment_id: `12`
- text: Two-stage training mechanism is previously applied on bilinear model in fine-grained visual recognition BIBREF31, BIBREF32, BIBREF33. Two CNNs are deployed in the model. One is trained at first for coarse-graind features while freezing the parameter of the other. Then unfreeze the other one and train the entire model in a low learning rate for fetching fine-grained features. Inspired by this and due to the large amount of parameters in BERT model, to speed up the training process, we fine tune the BERT model with new prediction layer first to achieve a better contextualized representation performance. Then we deploy the proposed model and load the fine tuned BERT weights, attach named entity information layers and retrain the model.

- section: `Experimental Studies`
- segment_id: `13`
- text: In this section, we devote to experimentally evaluating our proposed task and approach. The best results in tables are in bold.

- section: `Experimental Studies ::: Dataset and Evaluation Metrics`
- segment_id: `14`
- text: Our dataset is annotated based on Chinese pathology reports provided by the Department of Gastrointestinal Surgery, Ruijin Hospital. It contains 17,833 sentences, 826,987 characters and 2,714 question-answer pairs. All question-answer pairs are annotated and reviewed by four clinicians with three types of questions, namely tumor size, proximal resection margin and distal resection margin. These annotated instances have been partitioned into 1,899 training instances (12,412 sentences) and 815 test instances (5,421 sentences). Each instance has one or several sentences. Detailed statistics of different types of entities are listed in Table TABREF20. In the following experiments, two widely-used performance measures (i.e., EM-score BIBREF34 and (macro-averaged) F$_1$-score BIBREF35) are used to evaluate the methods. The Exact Match (EM-score) metric measures the percentage of predictions that match any one of the ground truth answers exactly. The F$_1$-score metric is a looser metric measures the average overlap between the prediction and ground truth answer.

- section: `Experimental Studies ::: Experimental Settings`
- segment_id: `15`
- text: To implement deep neural network models, we utilize the Keras library BIBREF36 with TensorFlow BIBREF37 backend. Each model is run on a single NVIDIA GeForce GTX 1080 Ti GPU. The models are trained by Adam optimization algorithm BIBREF38 whose parameters are the same as the default settings except for learning rate set to $5\times 10^{-5}$. Batch size is set to 3 or 4 due to the lack of graphical memory. We select BERT-base as the pre-trained language model in this paper. Due to the high cost of pre-training BERT language model, we directly adopt parameters pre-trained by Google in Chinese general corpus. The named entity recognition is applied on both pathology report texts and query texts.

- section: `Conclusion`
- segment_id: `22`
- text: In this paper, we present a question answering based clinical text structuring (QA-CTS) task, which unifies different clinical text structuring tasks and utilize different datasets. A novel model is also proposed to integrate named entity information into a pre-trained language model and adapt it to QA-CTS task. Initially, sequential results of named entity recognition on both paragraph and query texts are integrated together. Contextualized representation on both paragraph and query texts are transformed by a pre-trained language model. Then, the integrated named entity information and contextualized representation are integrated together and fed into a feed forward network for final prediction. Experimental results on real-world dataset demonstrate that our proposed model competes favorably with strong baseline models in all three specific tasks. The shared task and shared model introduced by QA-CTS task has also been proved to be useful for improving the performance on most of the task-specific datasets. In conclusion, the best way to achieve the best performance for a specific dataset is to pre-train the model in multiple datasets and then fine tune it on the specific dataset.

- section: `Acknowledgment`
- segment_id: `23`
- text: We would like to thank Ting Li and Xizhou Hong (Ruijin Hospital) who have helped us very much in data fetching and data cleansing. This work is supported by the National Key R&D Program of China for “Precision Medical Research" (No. 2018YFC0910500).

### Bridge
- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `39`
- text: We can see that our new generated reviews do not share strong attributes with previous known categories of fake reviews. If anything, our fake reviews are more similar to genuine reviews than previous fake reviews. We thus conjecture that our NMT-Fake* fake reviews present a category of fake reviews that may go undetected on online review sites.
- bridge_detail: seed=`40`, total=`2.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`1.000`

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `40`
- text: \subsection{Comparative user study} \label{sec:comparison} We wanted to evaluate the effectiveness of fake reviews againsttech-savvy users who understand and know to expect machine-generated fake reviews. We conducted a user study with 20 participants, all with computer science education and at least one university degree. Participant demographics are shown in Table~/ref{table:amt_pop} in the Appendix. Each participant first attended a training session where they were asked to label reviews (fake and genuine) and could later compare them to the correct answers -- we call these participants \emph{experienced participants}. No personal data was collected during the user study.
- bridge_detail: seed segment or not added via bridge scoring

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `41`
- text: Each person was given two randomly selected sets of 30 of reviews (a total of 60 reviews per person) with reviews containing 10 \textendash 50 words each. Each set contained 26 (87\%) real reviews from Yelp and 4 (13\%) machine-generated reviews, numbers chosen based on suspicious review prevalence on Yelp~/cite{mukherjee2013yelp,rayana2015collective}. One set contained machine-generated reviews from one of the two models (NMT ($b=0.3, \lambda=-5$) or LSTM), and the other set reviews from the other in randomized order. The number of fake reviews was revealed to each participant in the study description. Each participant was requested to mark four (4) reviews as fake.
- bridge_detail: seed=`40`, total=`2.100`, adjacency=`1.000`, entity_overlap=`0.100`, section_continuity=`1.000`

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `57`
- text: In this paper, we showed that neural machine translation models can be used to generate fake reviews that are very effective in deceiving even experienced, tech-savvy users. This supports anecdotal evidence \cite{national2017commission}. Our technique is more effective than state-of-the-art \cite{yao2017automated}. We conclude that machine-aided fake review detection is necessary since human users are ineffective in identifying fake reviews. We also showed that detectors trained using one type of fake reviews are not effective in identifying other types of fake reviews. Robust detection of fake reviews is thus still an open problem.
- bridge_detail: seed=`58`, total=`2.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`1.000`

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `58`
- text: \section*{Acknowledgments} We thank Tommi Gr\"{o}ndahl for assistance in planning user studies and the participants of the user study for their time and feedback. We also thank Luiza Sayfullina for comments that improved the manuscript. We thank the authors of \cite{yao2017automated} for answering questions about their work.
- bridge_detail: seed segment or not added via bridge scoring

- section: `5 Public House Las Vegas NV Gastropubs Restaurants > Excellent`
- segment_id: `59`
- text: \bibliographystyle{splncs} \begin{thebibliography}{10} \bibitem{yao2017automated} Yao, Y., Viswanath, B., Cryan, J., Zheng, H., Zhao, B.Y.: \newblock Automated crowdturfing attacks and defenses in online review systems. \newblock In: Proceedings of the 2017 ACM SIGSAC Conference on Computer and Communications Security, ACM (2017)
- bridge_detail: seed=`58`, total=`2.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`1.000`

- section: `The Proposed Model for QA-CTS Task ::: Two-Stage Training Mechanism`
- segment_id: `12`
- text: Two-stage training mechanism is previously applied on bilinear model in fine-grained visual recognition BIBREF31, BIBREF32, BIBREF33. Two CNNs are deployed in the model. One is trained at first for coarse-graind features while freezing the parameter of the other. Then unfreeze the other one and train the entire model in a low learning rate for fetching fine-grained features. Inspired by this and due to the large amount of parameters in BERT model, to speed up the training process, we fine tune the BERT model with new prediction layer first to achieve a better contextualized representation performance. Then we deploy the proposed model and load the fine tuned BERT weights, attach named entity information layers and retrain the model.
- bridge_detail: seed=`13`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Experimental Studies`
- segment_id: `13`
- text: In this section, we devote to experimentally evaluating our proposed task and approach. The best results in tables are in bold.
- bridge_detail: seed=`14`, total=`1.067`, adjacency=`1.000`, entity_overlap=`0.067`, section_continuity=`0.000`

- section: `Experimental Studies ::: Dataset and Evaluation Metrics`
- segment_id: `14`
- text: Our dataset is annotated based on Chinese pathology reports provided by the Department of Gastrointestinal Surgery, Ruijin Hospital. It contains 17,833 sentences, 826,987 characters and 2,714 question-answer pairs. All question-answer pairs are annotated and reviewed by four clinicians with three types of questions, namely tumor size, proximal resection margin and distal resection margin. These annotated instances have been partitioned into 1,899 training instances (12,412 sentences) and 815 test instances (5,421 sentences). Each instance has one or several sentences. Detailed statistics of different types of entities are listed in Table TABREF20. In the following experiments, two widely-used performance measures (i.e., EM-score BIBREF34 and (macro-averaged) F$_1$-score BIBREF35) are used to evaluate the methods. The Exact Match (EM-score) metric measures the percentage of predictions that match any one of the ground truth answers exactly. The F$_1$-score metric is a looser metric measures the average overlap between the prediction and ground truth answer.
- bridge_detail: seed=`13`, total=`1.067`, adjacency=`1.000`, entity_overlap=`0.067`, section_continuity=`0.000`

- section: `Experimental Studies ::: Experimental Settings`
- segment_id: `15`
- text: To implement deep neural network models, we utilize the Keras library BIBREF36 with TensorFlow BIBREF37 backend. Each model is run on a single NVIDIA GeForce GTX 1080 Ti GPU. The models are trained by Adam optimization algorithm BIBREF38 whose parameters are the same as the default settings except for learning rate set to $5\times 10^{-5}$. Batch size is set to 3 or 4 due to the lack of graphical memory. We select BERT-base as the pre-trained language model in this paper. Due to the high cost of pre-training BERT language model, we directly adopt parameters pre-trained by Google in Chinese general corpus. The named entity recognition is applied on both pathology report texts and query texts.
- bridge_detail: seed=`14`, total=`1.111`, adjacency=`1.000`, entity_overlap=`0.111`, section_continuity=`0.000`

- section: `Conclusion`
- segment_id: `22`
- text: In this paper, we present a question answering based clinical text structuring (QA-CTS) task, which unifies different clinical text structuring tasks and utilize different datasets. A novel model is also proposed to integrate named entity information into a pre-trained language model and adapt it to QA-CTS task. Initially, sequential results of named entity recognition on both paragraph and query texts are integrated together. Contextualized representation on both paragraph and query texts are transformed by a pre-trained language model. Then, the integrated named entity information and contextualized representation are integrated together and fed into a feed forward network for final prediction. Experimental results on real-world dataset demonstrate that our proposed model competes favorably with strong baseline models in all three specific tasks. The shared task and shared model introduced by QA-CTS task has also been proved to be useful for improving the performance on most of the task-specific datasets. In conclusion, the best way to achieve the best performance for a specific dataset is to pre-train the model in multiple datasets and then fine tune it on the specific dataset.
- bridge_detail: seed=`23`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Acknowledgment`
- segment_id: `23`
- text: We would like to thank Ting Li and Xizhou Hong (Ruijin Hospital) who have helped us very much in data fetching and data cleansing. This work is supported by the National Key R&D Program of China for “Precision Medical Research" (No. 2018YFC0910500).
- bridge_detail: seed segment or not added via bridge scoring

## Example 3

- paper_id: `1909.00694`
- question: How are relations used to propagate polarity?
- gold evidence:
  - In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive). Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event.
  - The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- note: Bridge seems to do about the same here based on the current evidence-hit proxy.

### Flat
- section: `Introduction`
- segment_id: `1`
- text: Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japanese web corpus. Given the minimum amount of supervision, they performed well. In addition, the combination of annotated and unannotated data yielded a gain over a purely supervised baseline when labeled data were small.

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.

- section: `Introduction`
- segment_id: `0`
- text: Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive). Learning affective events is challenging because, as the examples above suggest, the polarity of an event is not necessarily predictable from its constituent words. Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowledge, which can hardly be learned from small annotated data. In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive).

- section: `Related Work`
- segment_id: `2`
- text: Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movies), we work on how people are typically affected by events. In sentiment analysis, much attention has been paid to compositionality. Word-level polarity BIBREF5, BIBREF6, BIBREF7 and the roles of negation and intensification BIBREF8, BIBREF6, BIBREF9 are among the most important topics. In contrast, we are more interested in recognizing the sentiment polarity of an event that pertains to commonsense knowledge (e.g., getting money and catching cold). Label propagation from seed instances is a common approach to inducing sentiment polarities. While BIBREF5 and BIBREF10 worked on word- and phrase-level polarities, BIBREF0 dealt with event-level polarities. BIBREF5 and BIBREF10 linked instances using co-occurrence information and/or phrase-level coordinations (e.g., “$A$ and $B$” and “$A$ but $B$”).

- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.

### Adjacency
- section: `Introduction`
- segment_id: `0`
- text: Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive). Learning affective events is challenging because, as the examples above suggest, the polarity of an event is not necessarily predictable from its constituent words. Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowledge, which can hardly be learned from small annotated data. In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive).

- section: `Introduction`
- segment_id: `1`
- text: Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japanese web corpus. Given the minimum amount of supervision, they performed well. In addition, the combination of annotated and unannotated data yielded a gain over a purely supervised baseline when labeled data were small.

- section: `Related Work`
- segment_id: `2`
- text: Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movies), we work on how people are typically affected by events. In sentiment analysis, much attention has been paid to compositionality. Word-level polarity BIBREF5, BIBREF6, BIBREF7 and the roles of negation and intensification BIBREF8, BIBREF6, BIBREF9 are among the most important topics. In contrast, we are more interested in recognizing the sentiment polarity of an event that pertains to commonsense knowledge (e.g., getting money and catching cold). Label propagation from seed instances is a common approach to inducing sentiment polarities. While BIBREF5 and BIBREF10 worked on word- and phrase-level polarities, BIBREF0 dealt with event-level polarities. BIBREF5 and BIBREF10 linked instances using co-occurrence information and/or phrase-level coordinations (e.g., “$A$ and $B$” and “$A$ but $B$”).

- section: `Related Work`
- segment_id: `3`
- text: We shift our scope to event pairs that are more complex than phrase pairs, and consequently exploit discourse connectives as event-level counterparts of phrase-level conjunctions. BIBREF0 constructed a network of events using word embedding-derived similarities. Compared with this method, our discourse relation-based linking of events is much simpler and more intuitive. Some previous studies made use of document structure to understand the sentiment. BIBREF11 proposed a sentiment-specific pre-training strategy using unlabeled dialog data (tweet-reply pairs). BIBREF12 proposed a method of building a polarity-tagged corpus (ACP Corpus). They automatically gathered sentences that had positive or negative opinions utilizing HTML layout structures in addition to linguistic patterns. Our method depends only on raw texts and thus has wider applicability.

- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.

### Bridge
- section: `Introduction`
- segment_id: `0`
- text: Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive). Learning affective events is challenging because, as the examples above suggest, the polarity of an event is not necessarily predictable from its constituent words. Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowledge, which can hardly be learned from small annotated data. In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive).
- bridge_detail: seed=`1`, total=`2.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`1.000`

- section: `Introduction`
- segment_id: `1`
- text: Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japanese web corpus. Given the minimum amount of supervision, they performed well. In addition, the combination of annotated and unannotated data yielded a gain over a purely supervised baseline when labeled data were small.
- bridge_detail: seed=`0`, total=`2.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`1.000`

- section: `Related Work`
- segment_id: `2`
- text: Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movies), we work on how people are typically affected by events. In sentiment analysis, much attention has been paid to compositionality. Word-level polarity BIBREF5, BIBREF6, BIBREF7 and the roles of negation and intensification BIBREF8, BIBREF6, BIBREF9 are among the most important topics. In contrast, we are more interested in recognizing the sentiment polarity of an event that pertains to commonsense knowledge (e.g., getting money and catching cold). Label propagation from seed instances is a common approach to inducing sentiment polarities. While BIBREF5 and BIBREF10 worked on word- and phrase-level polarities, BIBREF0 dealt with event-level polarities. BIBREF5 and BIBREF10 linked instances using co-occurrence information and/or phrase-level coordinations (e.g., “$A$ and $B$” and “$A$ but $B$”).
- bridge_detail: seed=`1`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Related Work`
- segment_id: `3`
- text: We shift our scope to event pairs that are more complex than phrase pairs, and consequently exploit discourse connectives as event-level counterparts of phrase-level conjunctions. BIBREF0 constructed a network of events using word embedding-derived similarities. Compared with this method, our discourse relation-based linking of events is much simpler and more intuitive. Some previous studies made use of document structure to understand the sentiment. BIBREF11 proposed a sentiment-specific pre-training strategy using unlabeled dialog data (tweet-reply pairs). BIBREF12 proposed a method of building a polarity-tagged corpus (ACP Corpus). They automatically gathered sentences that had positive or negative opinions utilizing HTML layout structures in addition to linguistic patterns. Our method depends only on raw texts and thus has wider applicability.
- bridge_detail: seed=`2`, total=`2.050`, adjacency=`1.000`, entity_overlap=`0.050`, section_continuity=`1.000`

- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- bridge_detail: seed=`4`, total=`1.111`, adjacency=`1.000`, entity_overlap=`0.111`, section_continuity=`0.000`

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.
- bridge_detail: seed=`17`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.
- bridge_detail: seed=`17`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

## Example 4

- paper_id: `1909.00694`
- question: How big is the Japanese data?
- gold evidence:
  - As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction.
  - We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
  - FLOAT SELECTED: Table 1: Statistics of the AL, CA, and CO datasets.
  - We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively:
  - Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19.
  - FLOAT SELECTED: Table 2: Details of the ACP dataset.
- note: Bridge seems to do about the same here based on the current evidence-hit proxy.

### Flat
- section: `Appendices ::: Settings of Encoder ::: BERT`
- segment_id: `22`
- text: We used a Japanese BERT model pretrained with Japanese Wikipedia. The input sentences were segmented into words by Juman++, and words were broken into subwords by applying BPE BIBREF20. The vocabulary size was 32,000. The maximum length of an input sequence was 128. The number of hidden layers was 12. The dimension of hidden units was 768. The number of self-attention heads was 12. The optimizer was Adam BIBREF19. The mini-batch size was 32. We ran 1 epoch.

- section: `Appendices ::: Settings of Encoder ::: BiGRU`
- segment_id: `21`
- text: The dimension of the embedding layer was 256. The embedding layer was initialized with the word embeddings pretrained using the Web corpus. The input sentences were segmented into words by the morphological analyzer Juman++. The vocabulary size was 100,000. The number of hidden layers was 2. The dimension of hidden units was 256. The optimizer was Momentum SGD BIBREF21. The mini-batch size was 1024. We ran 100 epochs and selected the snapshot that achieved the highest score for the dev set.

- section: `Semantic Representations ::: Experiments ::: FastText Training and Evaluation`
- segment_id: `17`
- text: As a first experiment, we compare the quality of fastText embeddings trained on (high-quality) curated data and (low-quality) massively extracted data for Twi and Yorùbá languages. Facebook released pre-trained word embeddings using fastText for 294 languages trained on Wikipedia BIBREF2 (F1 in tables) and for 157 languages trained on Wikipedia and Common Crawl BIBREF7 (F2). For Yorùbá, both versions are available but only embeddings trained on Wikipedia are available for Twi. We consider these embeddings the result of training on what we call massively-extracted corpora. Notice that training settings for both embeddings are not exactly the same, and differences in performance might come both from corpus size/quality but also from the background model. The 294-languages version is trained using skipgram, in dimension 300, with character $n$-grams of length 5, a window of size 5 and 5 negatives. The 157-languages version is trained using CBOW with position-weights, in dimension 300, with character $n$-grams of length 5, a window of size 5 and 10 negatives. We want to compare the performance of these embeddings with the equivalent models that can be obtained by training on the different sources verified by native speakers of Twi and Yorùbá; what we call curated corpora and has been described in Section SECREF4 For the comparison, we define 3 datasets according to the quality and quantity of textual data used for training: (i) Curated Small Dataset (clean), C1, about 1.6 million tokens for Yorùbá and over 735 k tokens for Twi. The clean text for Twi is the Bible and for Yoruba all texts marked under the C1 column in Table TABREF7. (ii) In Curated Small Dataset (clean + noisy), C2, we add noise to the clean corpus (Wikipedia articles for Twi, and BBC Yorùbá news articles for Yorùbá). This increases the number of training tokens for Twi to 742 k tokens and Yorùbá to about 2 million tokens. (iii) Curated Large Dataset, C3 consists of all available texts we are able to crawl and source out for, either clean or noisy. The addition of JW300 BIBREF22 texts increases the vocabulary to more than 10 k tokens in both languages. We train our fastText systems using a skipgram model with an embedding size of 300 dimensions, context window size of 5, 10 negatives and $n$-grams ranging from 3 to 6 characters similarly to the pre-trained models for both languages. Best results are obtained with minimum word count of 3. Table TABREF15 shows the Spearman correlation between human judgements and cosine similarity scores on the wordSim-353 test set.

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.

- section: `Summary and Discussion`
- segment_id: `24`
- text: In a low-resourced setting, the data quality, processing and model selection is more critical than in a high-resourced scenario. We show how the characteristics of a language (such as diacritization in our case) should be taken into account in order to choose the relevant data and model to use. As an example, Twi word embeddings are significantly better when training on 742 k selected tokens than on 16 million noisy tokens, and when using a model that takes into account single character information (CWE-LP) instead of $n$-gram information (fastText). Finally, we want to note that, even within a corpus, the quality of the data might depend on the language. Wikipedia is usually used as a high-quality freely available multilingual corpus as compared to noisier data such as Common Crawl. However, for the two languages under study, Wikipedia resulted to have too much noise: interference from other languages, text clearly written by non-native speakers, lack of diacritics and mixture of dialects. The JW300 corpus on the other hand, has been rated as high-quality by our native Yorùbá speakers, but as noisy by our native Twi speakers. In both cases, experiments confirm the conclusions.

### Adjacency
- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.

- section: `Appendices ::: Seed Lexicon ::: Positive Words`
- segment_id: `19`
- text: 喜ぶ (rejoice), 嬉しい (be glad), 楽しい (be pleasant), 幸せ (be happy), 感動 (be impressed), 興奮 (be excited), 懐かしい (feel nostalgic), 好き (like), 尊敬 (respect), 安心 (be relieved), 感心 (admire), 落ち着く (be calm), 満足 (be satisfied), 癒される (be healed), and スッキリ (be refreshed).

- section: `Appendices ::: Seed Lexicon ::: Negative Words`
- segment_id: `20`
- text: 怒る (get angry), 悲しい (be sad), 寂しい (be lonely), 怖い (be scared), 不安 (feel anxious), 恥ずかしい (be embarrassed), 嫌 (hate), 落ち込む (feel down), 退屈 (be bored), 絶望 (feel hopeless), 辛い (have a hard time), 困る (have trouble), 憂鬱 (be depressed), 心配 (be worried), and 情けない (be sorry).

- section: `Appendices ::: Settings of Encoder ::: BiGRU`
- segment_id: `21`
- text: The dimension of the embedding layer was 256. The embedding layer was initialized with the word embeddings pretrained using the Web corpus. The input sentences were segmented into words by the morphological analyzer Juman++. The vocabulary size was 100,000. The number of hidden layers was 2. The dimension of hidden units was 256. The optimizer was Momentum SGD BIBREF21. The mini-batch size was 1024. We ran 100 epochs and selected the snapshot that achieved the highest score for the dev set.

- section: `Appendices ::: Settings of Encoder ::: BERT`
- segment_id: `22`
- text: We used a Japanese BERT model pretrained with Japanese Wikipedia. The input sentences were segmented into words by Juman++, and words were broken into subwords by applying BPE BIBREF20. The vocabulary size was 32,000. The maximum length of an input sequence was 128. The number of hidden layers was 12. The dimension of hidden units was 768. The number of self-attention heads was 12. The optimizer was Adam BIBREF19. The mini-batch size was 32. We ran 1 epoch.

- section: `Semantic Representations ::: Word Embeddings Architectures`
- segment_id: `16`
- text: cwe also proposed three alternatives to learn multiple embeddings per character and resolve ambiguities: (i) position-based character embeddings where each character has different embeddings depending on the position it appears in a word, i.e., beginning, middle or end (ii) cluster-based character embeddings where a character can have $K$ different cluster embeddings, and (iii) position-based cluster embeddings (CWE-LP) where for each position $K$ different embeddings are learned. We use the latter in our experiments with CWE but no positional embeddings are used with fastText. Finally, we consider a contextualized embedding architecture, BERT BIBREF4. BERT is a masked language model based on the highly efficient and parallelizable Transformer architecture BIBREF21 known to produce very rich contextualized representations for downstream NLP tasks. The architecture is trained by jointly conditioning on both left and right contexts in all the transformer layers using two unsupervised objectives: Masked LM and Next-sentence prediction. The representation of a word is therefore learned according to the context it is found in. Training contextual embeddings needs of huge amounts of corpora which are not available for low-resourced languages such as Yorùbá and Twi. However, Google provided pre-trained multilingual embeddings for 102 languages including Yorùbá (but not Twi).

- section: `Semantic Representations ::: Experiments ::: FastText Training and Evaluation`
- segment_id: `17`
- text: As a first experiment, we compare the quality of fastText embeddings trained on (high-quality) curated data and (low-quality) massively extracted data for Twi and Yorùbá languages. Facebook released pre-trained word embeddings using fastText for 294 languages trained on Wikipedia BIBREF2 (F1 in tables) and for 157 languages trained on Wikipedia and Common Crawl BIBREF7 (F2). For Yorùbá, both versions are available but only embeddings trained on Wikipedia are available for Twi. We consider these embeddings the result of training on what we call massively-extracted corpora. Notice that training settings for both embeddings are not exactly the same, and differences in performance might come both from corpus size/quality but also from the background model. The 294-languages version is trained using skipgram, in dimension 300, with character $n$-grams of length 5, a window of size 5 and 5 negatives. The 157-languages version is trained using CBOW with position-weights, in dimension 300, with character $n$-grams of length 5, a window of size 5 and 10 negatives. We want to compare the performance of these embeddings with the equivalent models that can be obtained by training on the different sources verified by native speakers of Twi and Yorùbá; what we call curated corpora and has been described in Section SECREF4 For the comparison, we define 3 datasets according to the quality and quantity of textual data used for training: (i) Curated Small Dataset (clean), C1, about 1.6 million tokens for Yorùbá and over 735 k tokens for Twi. The clean text for Twi is the Bible and for Yoruba all texts marked under the C1 column in Table TABREF7. (ii) In Curated Small Dataset (clean + noisy), C2, we add noise to the clean corpus (Wikipedia articles for Twi, and BBC Yorùbá news articles for Yorùbá). This increases the number of training tokens for Twi to 742 k tokens and Yorùbá to about 2 million tokens. (iii) Curated Large Dataset, C3 consists of all available texts we are able to crawl and source out for, either clean or noisy. The addition of JW300 BIBREF22 texts increases the vocabulary to more than 10 k tokens in both languages. We train our fastText systems using a skipgram model with an embedding size of 300 dimensions, context window size of 5, 10 negatives and $n$-grams ranging from 3 to 6 characters similarly to the pre-trained models for both languages. Best results are obtained with minimum word count of 3. Table TABREF15 shows the Spearman correlation between human judgements and cosine similarity scores on the wordSim-353 test set.

- section: `Semantic Representations ::: Experiments ::: FastText Training and Evaluation`
- segment_id: `18`
- text: Notice that pre-trained embeddings on Wikipedia show a very low correlation with humans on the similarity task for both languages ($\rho $=$0.14$) and their performance is even lower when Common Crawl is also considered ($\rho $=$0.07$ for Yorùbá). An important reason for the low performance is the limited vocabulary. The pre-trained Twi model has only 935 tokens. For Yorùbá, things are apparently better with more than 150 k tokens when both Wikipedia and Common Crawl are used but correlation is even lower. An inspection of the pre-trained embeddings indicates that over 135 k words belong to other languages mostly English, French and Arabic. If we focus only on Wikipedia, we see that many texts are without diacritics in Yorùbá and often make use of mixed dialects and English sentences in Twi. The Spearman $\rho $ correlation for fastText models on the curated small dataset (clean), C1, improves the baselines by a large margin ($\rho =0.354$ for Twi and 0.322 for Yorùbá) even with a small dataset. The improvement could be justified just by the larger vocabulary in Twi, but in the case of Yorùbá the enhancement is there with almost half of the vocabulary size. We found out that adding some noisy texts (C2 dataset) slightly improves the correlation for Twi language but not for the Yorùbá language. The Twi language benefits from Wikipedia articles because its inclusion doubles the vocabulary and reduces the bias of the model towards religious texts. However, for Yorùbá, noisy texts often ignore diacritics or tonal marks which increases the vocabulary size at the cost of an increment in the ambiguity too. As a result, the correlation is slightly hurt. One would expect that training with more data would improve the quality of the embeddings, but we found out with the results obtained with the C3 dataset, that only high-quality data helps. The addition of JW300 boosts the vocabulary in both cases, but whereas for Twi the corpus mixes dialects and is noisy, for Yorùbá it is very clean and with full diacritics. Consequently, the best embeddings for Yorùbá are obtained when training with the C3 dataset, whereas for Twi, C2 is the best option. In both cases, the curated embeddings improve the correlation with human judgements on the similarity task a $\Delta \rho =+0.25$ or, equivalently, by an increment on $\rho $ of 170% (Twi) and 180% (Yorùbá).

- section: `Summary and Discussion`
- segment_id: `23`
- text: In this paper, we present curated word and contextual embeddings for Yorùbá and Twi. For this purpose, we gather and select corpora and study the most appropriate techniques for the languages. We also create test sets for the evaluation of the word embeddings within a word similarity task (wordsim353) and the contextual embeddings within a NER task. Corpora, embeddings and test sets are available in github. In our analysis, we show how massively generated embeddings perform poorly for low-resourced languages as compared to the performance for high-resourced ones. This is due both to the quantity but also the quality of the data used. While the Pearson $\rho $ correlation for English obtained with fastText embeddings trained on Wikipedia (WP) and Common Crawl (CC) are $\rho _{WP}$=$0.67$ and $\rho _{WP+CC}$=$0.78$, the equivalent ones for Yorùbá are $\rho _{WP}$=$0.14$ and $\rho _{WP+CC}$=$0.07$. For Twi, only embeddings with Wikipedia are available ($\rho _{WP}$=$0.14$). By carefully gathering high-quality data and optimising the models to the characteristics of each language, we deliver embeddings with correlations of $\rho $=$0.39$ (Yorùbá) and $\rho $=$0.44$ (Twi) on the same test set, still far from the high-resourced models, but representing an improvement over $170\%$ on the task.

- section: `Summary and Discussion`
- segment_id: `24`
- text: In a low-resourced setting, the data quality, processing and model selection is more critical than in a high-resourced scenario. We show how the characteristics of a language (such as diacritization in our case) should be taken into account in order to choose the relevant data and model to use. As an example, Twi word embeddings are significantly better when training on 742 k selected tokens than on 16 million noisy tokens, and when using a model that takes into account single character information (CWE-LP) instead of $n$-gram information (fastText). Finally, we want to note that, even within a corpus, the quality of the data might depend on the language. Wikipedia is usually used as a high-quality freely available multilingual corpus as compared to noisier data such as Common Crawl. However, for the two languages under study, Wikipedia resulted to have too much noise: interference from other languages, text clearly written by non-native speakers, lack of diacritics and mixture of dialects. The JW300 corpus on the other hand, has been rated as high-quality by our native Yorùbá speakers, but as noisy by our native Twi speakers. In both cases, experiments confirm the conclusions.

- section: `Acknowledgements`
- segment_id: `25`
- text: The authors thank Dr. Clement Odoje of the Department of Linguistics and African Languages, University of Ibadan, Nigeria and Olóyè Gbémisóyè Àrdèó for helping us with the Yorùbá translation of the WordSim-353 word pairs and Dr. Felix Y. Adu-Gyamfi and Ps. Isaac Sarfo for helping with the Twi translation. We also thank the members of the Niger-Volta Language Technologies Institute for providing us with clean Yorùbá corpus The project on which this paper is based was partially funded by the German Federal Ministry of Education and Research under the funding code 01IW17001 (Deeplee). Responsibility for the content of this publication is with the authors.

### Bridge
- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.
- bridge_detail: seed=`18`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Appendices ::: Seed Lexicon ::: Positive Words`
- segment_id: `19`
- text: 喜ぶ (rejoice), 嬉しい (be glad), 楽しい (be pleasant), 幸せ (be happy), 感動 (be impressed), 興奮 (be excited), 懐かしい (feel nostalgic), 好き (like), 尊敬 (respect), 安心 (be relieved), 感心 (admire), 落ち着く (be calm), 満足 (be satisfied), 癒される (be healed), and スッキリ (be refreshed).
- bridge_detail: seed=`18`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Appendices ::: Seed Lexicon ::: Negative Words`
- segment_id: `20`
- text: 怒る (get angry), 悲しい (be sad), 寂しい (be lonely), 怖い (be scared), 不安 (feel anxious), 恥ずかしい (be embarrassed), 嫌 (hate), 落ち込む (feel down), 退屈 (be bored), 絶望 (feel hopeless), 辛い (have a hard time), 困る (have trouble), 憂鬱 (be depressed), 心配 (be worried), and 情けない (be sorry).
- bridge_detail: seed=`21`, total=`1.000`, adjacency=`1.000`, entity_overlap=`0.000`, section_continuity=`0.000`

- section: `Appendices ::: Settings of Encoder ::: BiGRU`
- segment_id: `21`
- text: The dimension of the embedding layer was 256. The embedding layer was initialized with the word embeddings pretrained using the Web corpus. The input sentences were segmented into words by the morphological analyzer Juman++. The vocabulary size was 100,000. The number of hidden layers was 2. The dimension of hidden units was 256. The optimizer was Momentum SGD BIBREF21. The mini-batch size was 1024. We ran 100 epochs and selected the snapshot that achieved the highest score for the dev set.
- bridge_detail: seed=`22`, total=`1.250`, adjacency=`1.000`, entity_overlap=`0.250`, section_continuity=`0.000`

- section: `Appendices ::: Settings of Encoder ::: BERT`
- segment_id: `22`
- text: We used a Japanese BERT model pretrained with Japanese Wikipedia. The input sentences were segmented into words by Juman++, and words were broken into subwords by applying BPE BIBREF20. The vocabulary size was 32,000. The maximum length of an input sequence was 128. The number of hidden layers was 12. The dimension of hidden units was 768. The number of self-attention heads was 12. The optimizer was Adam BIBREF19. The mini-batch size was 32. We ran 1 epoch.
- bridge_detail: seed=`21`, total=`1.250`, adjacency=`1.000`, entity_overlap=`0.250`, section_continuity=`0.000`

- section: `Semantic Representations ::: Word Embeddings Architectures`
- segment_id: `16`
- text: cwe also proposed three alternatives to learn multiple embeddings per character and resolve ambiguities: (i) position-based character embeddings where each character has different embeddings depending on the position it appears in a word, i.e., beginning, middle or end (ii) cluster-based character embeddings where a character can have $K$ different cluster embeddings, and (iii) position-based cluster embeddings (CWE-LP) where for each position $K$ different embeddings are learned. We use the latter in our experiments with CWE but no positional embeddings are used with fastText. Finally, we consider a contextualized embedding architecture, BERT BIBREF4. BERT is a masked language model based on the highly efficient and parallelizable Transformer architecture BIBREF21 known to produce very rich contextualized representations for downstream NLP tasks. The architecture is trained by jointly conditioning on both left and right contexts in all the transformer layers using two unsupervised objectives: Masked LM and Next-sentence prediction. The representation of a word is therefore learned according to the context it is found in. Training contextual embeddings needs of huge amounts of corpora which are not available for low-resourced languages such as Yorùbá and Twi. However, Google provided pre-trained multilingual embeddings for 102 languages including Yorùbá (but not Twi).
- bridge_detail: seed=`17`, total=`1.086`, adjacency=`1.000`, entity_overlap=`0.086`, section_continuity=`0.000`

- section: `Semantic Representations ::: Experiments ::: FastText Training and Evaluation`
- segment_id: `17`
- text: As a first experiment, we compare the quality of fastText embeddings trained on (high-quality) curated data and (low-quality) massively extracted data for Twi and Yorùbá languages. Facebook released pre-trained word embeddings using fastText for 294 languages trained on Wikipedia BIBREF2 (F1 in tables) and for 157 languages trained on Wikipedia and Common Crawl BIBREF7 (F2). For Yorùbá, both versions are available but only embeddings trained on Wikipedia are available for Twi. We consider these embeddings the result of training on what we call massively-extracted corpora. Notice that training settings for both embeddings are not exactly the same, and differences in performance might come both from corpus size/quality but also from the background model. The 294-languages version is trained using skipgram, in dimension 300, with character $n$-grams of length 5, a window of size 5 and 5 negatives. The 157-languages version is trained using CBOW with position-weights, in dimension 300, with character $n$-grams of length 5, a window of size 5 and 10 negatives. We want to compare the performance of these embeddings with the equivalent models that can be obtained by training on the different sources verified by native speakers of Twi and Yorùbá; what we call curated corpora and has been described in Section SECREF4 For the comparison, we define 3 datasets according to the quality and quantity of textual data used for training: (i) Curated Small Dataset (clean), C1, about 1.6 million tokens for Yorùbá and over 735 k tokens for Twi. The clean text for Twi is the Bible and for Yoruba all texts marked under the C1 column in Table TABREF7. (ii) In Curated Small Dataset (clean + noisy), C2, we add noise to the clean corpus (Wikipedia articles for Twi, and BBC Yorùbá news articles for Yorùbá). This increases the number of training tokens for Twi to 742 k tokens and Yorùbá to about 2 million tokens. (iii) Curated Large Dataset, C3 consists of all available texts we are able to crawl and source out for, either clean or noisy. The addition of JW300 BIBREF22 texts increases the vocabulary to more than 10 k tokens in both languages. We train our fastText systems using a skipgram model with an embedding size of 300 dimensions, context window size of 5, 10 negatives and $n$-grams ranging from 3 to 6 characters similarly to the pre-trained models for both languages. Best results are obtained with minimum word count of 3. Table TABREF15 shows the Spearman correlation between human judgements and cosine similarity scores on the wordSim-353 test set.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Semantic Representations ::: Experiments ::: FastText Training and Evaluation`
- segment_id: `18`
- text: Notice that pre-trained embeddings on Wikipedia show a very low correlation with humans on the similarity task for both languages ($\rho $=$0.14$) and their performance is even lower when Common Crawl is also considered ($\rho $=$0.07$ for Yorùbá). An important reason for the low performance is the limited vocabulary. The pre-trained Twi model has only 935 tokens. For Yorùbá, things are apparently better with more than 150 k tokens when both Wikipedia and Common Crawl are used but correlation is even lower. An inspection of the pre-trained embeddings indicates that over 135 k words belong to other languages mostly English, French and Arabic. If we focus only on Wikipedia, we see that many texts are without diacritics in Yorùbá and often make use of mixed dialects and English sentences in Twi. The Spearman $\rho $ correlation for fastText models on the curated small dataset (clean), C1, improves the baselines by a large margin ($\rho =0.354$ for Twi and 0.322 for Yorùbá) even with a small dataset. The improvement could be justified just by the larger vocabulary in Twi, but in the case of Yorùbá the enhancement is there with almost half of the vocabulary size. We found out that adding some noisy texts (C2 dataset) slightly improves the correlation for Twi language but not for the Yorùbá language. The Twi language benefits from Wikipedia articles because its inclusion doubles the vocabulary and reduces the bias of the model towards religious texts. However, for Yorùbá, noisy texts often ignore diacritics or tonal marks which increases the vocabulary size at the cost of an increment in the ambiguity too. As a result, the correlation is slightly hurt. One would expect that training with more data would improve the quality of the embeddings, but we found out with the results obtained with the C3 dataset, that only high-quality data helps. The addition of JW300 boosts the vocabulary in both cases, but whereas for Twi the corpus mixes dialects and is noisy, for Yorùbá it is very clean and with full diacritics. Consequently, the best embeddings for Yorùbá are obtained when training with the C3 dataset, whereas for Twi, C2 is the best option. In both cases, the curated embeddings improve the correlation with human judgements on the similarity task a $\Delta \rho =+0.25$ or, equivalently, by an increment on $\rho $ of 170% (Twi) and 180% (Yorùbá).
- bridge_detail: seed=`17`, total=`2.182`, adjacency=`1.000`, entity_overlap=`0.182`, section_continuity=`1.000`

- section: `Summary and Discussion`
- segment_id: `23`
- text: In this paper, we present curated word and contextual embeddings for Yorùbá and Twi. For this purpose, we gather and select corpora and study the most appropriate techniques for the languages. We also create test sets for the evaluation of the word embeddings within a word similarity task (wordsim353) and the contextual embeddings within a NER task. Corpora, embeddings and test sets are available in github. In our analysis, we show how massively generated embeddings perform poorly for low-resourced languages as compared to the performance for high-resourced ones. This is due both to the quantity but also the quality of the data used. While the Pearson $\rho $ correlation for English obtained with fastText embeddings trained on Wikipedia (WP) and Common Crawl (CC) are $\rho _{WP}$=$0.67$ and $\rho _{WP+CC}$=$0.78$, the equivalent ones for Yorùbá are $\rho _{WP}$=$0.14$ and $\rho _{WP+CC}$=$0.07$. For Twi, only embeddings with Wikipedia are available ($\rho _{WP}$=$0.14$). By carefully gathering high-quality data and optimising the models to the characteristics of each language, we deliver embeddings with correlations of $\rho $=$0.39$ (Yorùbá) and $\rho $=$0.44$ (Twi) on the same test set, still far from the high-resourced models, but representing an improvement over $170\%$ on the task.
- bridge_detail: seed=`24`, total=`2.250`, adjacency=`1.000`, entity_overlap=`0.250`, section_continuity=`1.000`

- section: `Summary and Discussion`
- segment_id: `24`
- text: In a low-resourced setting, the data quality, processing and model selection is more critical than in a high-resourced scenario. We show how the characteristics of a language (such as diacritization in our case) should be taken into account in order to choose the relevant data and model to use. As an example, Twi word embeddings are significantly better when training on 742 k selected tokens than on 16 million noisy tokens, and when using a model that takes into account single character information (CWE-LP) instead of $n$-gram information (fastText). Finally, we want to note that, even within a corpus, the quality of the data might depend on the language. Wikipedia is usually used as a high-quality freely available multilingual corpus as compared to noisier data such as Common Crawl. However, for the two languages under study, Wikipedia resulted to have too much noise: interference from other languages, text clearly written by non-native speakers, lack of diacritics and mixture of dialects. The JW300 corpus on the other hand, has been rated as high-quality by our native Yorùbá speakers, but as noisy by our native Twi speakers. In both cases, experiments confirm the conclusions.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Acknowledgements`
- segment_id: `25`
- text: The authors thank Dr. Clement Odoje of the Department of Linguistics and African Languages, University of Ibadan, Nigeria and Olóyè Gbémisóyè Àrdèó for helping us with the Yorùbá translation of the WordSim-353 word pairs and Dr. Felix Y. Adu-Gyamfi and Ps. Isaac Sarfo for helping with the Twi translation. We also thank the members of the Niger-Volta Language Technologies Institute for providing us with clean Yorùbá corpus The project on which this paper is based was partially funded by the German Federal Ministry of Education and Research under the funding code 01IW17001 (Deeplee). Responsibility for the content of this publication is with the authors.
- bridge_detail: seed=`24`, total=`1.077`, adjacency=`1.000`, entity_overlap=`0.077`, section_continuity=`0.000`

## Example 5

- paper_id: `1909.00694`
- question: What are labels available in dataset for supervision?
- gold evidence:
  - Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive).
- note: Bridge seems to do about the same here based on the current evidence-hit proxy.

### Flat
- section: `Acknowledgements`
- segment_id: `30`
- text: A special thanks goes to Gesine Fuhrmann, who created the guidelines and tirelessly documented the annotation progress. Also thanks to Annika Palm and Debby Trzeciak who annotated and gave lively feedback. For help with the conceptualization of labels we thank Ines Schindler. This research has been partially conducted within the CRETA center (http://www.creta.uni-stuttgart.de/) which is funded by the German Ministry for Education and Research (BMBF) and partially funded by the German Research Council (DFG), projects SEAT (Structured Multi-Domain Emotion Analysis from Text, KL 2869/1-1). This work has also been supported by the German Research Foundation as part of the Research Training Group Adaptive Preparation of Information from Heterogeneous Sources (AIPHES) at the Technische Universität Darmstadt under grant No. GRK 1994/1.

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.

- section: `Modeling`
- segment_id: `26`
- text: To estimate the difficulty of automatic classification of our data set, we perform multi-label document classification (of stanzas) with BERT BIBREF41. For this experiment we aggregate all labels for a stanza and sort them by frequency, both for the gold standard and the raw expert annotations. As can be seen in Figure FIGREF23, a stanza bears a minimum of one and a maximum of four emotions. Unfortunately, the label Nostalgia is only available 16 times in the German data (the gold standard) as a second label (as discussed in Section SECREF19). None of our models was able to learn this label for German. Therefore we omit it, leaving us with eight proper labels. We use the code and the pre-trained BERT models of Farm, provided by deepset.ai. We test the multilingual-uncased model (Multiling), the german-base-cased model (Base), the german-dbmdz-uncased model (Dbmdz), and we tune the Base model on 80k stanzas of the German Poetry Corpus DLK BIBREF30 for 2 epochs, both on token (masked words) and sequence (next line) prediction (Base$_{\textsc {Tuned}}$). We split the randomized German dataset so that each label is at least 10 times in the validation set (63 instances, 113 labels), and at least 10 times in the test set (56 instances, 108 labels) and leave the rest for training (617 instances, 946 labels).

- section: `Related Work`
- segment_id: `2`
- text: There is a wide range of techniques that provide interesting results in the context of ML algorithms geared to the classification of data without discrimination; these techniques range from the pre-processing of data BIBREF4 to the use of bias removal techniques BIBREF5 in fact. Approaches linked to the data pre-processing step usually consist of methods based on improving the quality of the dataset after which the usual classification tools can be used to train a classifier. So, it starts from a baseline already stipulated by the execution of itself. On the other side of the spectrum, there are Unsupervised and semi-supervised learning techniques, that are attractive because they do not imply the cost of corpus annotation BIBREF6 , BIBREF7 , BIBREF8 , BIBREF9 . The bias reduction is studied as a way to reduce discrimination through classification through different approaches BIBREF10 BIBREF11 . In BIBREF12 the authors propose to specify, implement, and evaluate the “fairness-aware" ML interface called themis-ml. In this interface, the main idea is to pick up a data set from a modified dataset.

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:

### Adjacency
- section: `Introduction`
- segment_id: `1`
- text: This work aims to analyze and remove gender stereotypes from word embedding in Portuguese, analogous to what was done in BIBREF3 for the English language. Hence, we propose to employ a public word2vec model pre-trained to analyze gender bias in the Portuguese language, quantifying biases present in the model so that it is possible to reduce the spreading of sexism of such models. There is also a stage of bias reducing over the results obtained in the model, where it is sought to analyze the effects of the application of gender distinction reduction techniques. This paper is organized as follows: Section SECREF2 discusses related works. Section SECREF3 presents the Portuguese word2vec embeddings model used in this paper and Section SECREF4 proposes our method. Section SECREF5 presents experimental results, whose purpose is to verify results of a de-bias algorithm application in Portuguese embeddings word2vec model and a short discussion about it. Section SECREF6 brings our concluding remarks.

- section: `Related Work`
- segment_id: `2`
- text: There is a wide range of techniques that provide interesting results in the context of ML algorithms geared to the classification of data without discrimination; these techniques range from the pre-processing of data BIBREF4 to the use of bias removal techniques BIBREF5 in fact. Approaches linked to the data pre-processing step usually consist of methods based on improving the quality of the dataset after which the usual classification tools can be used to train a classifier. So, it starts from a baseline already stipulated by the execution of itself. On the other side of the spectrum, there are Unsupervised and semi-supervised learning techniques, that are attractive because they do not imply the cost of corpus annotation BIBREF6 , BIBREF7 , BIBREF8 , BIBREF9 . The bias reduction is studied as a way to reduce discrimination through classification through different approaches BIBREF10 BIBREF11 . In BIBREF12 the authors propose to specify, implement, and evaluate the “fairness-aware" ML interface called themis-ml. In this interface, the main idea is to pick up a data set from a modified dataset.

- section: `Related Work`
- segment_id: `3`
- text: Themis-ml implements two methods for training fairness-aware models. The tool relies on two methods to make agnostic model type predictions: Reject Option Classification and Discrimination-Aware Ensemble Classification, these procedures being used to post-process predictions in a way that reduces potentially discriminatory predictions. According to the authors, it is possible to perceive the potential use of the method as a means of reducing bias in the use of ML algorithms. In BIBREF3 , the authors propose a method to hardly reduce bias in English word embeddings collected from Google News. Using word2vec, they performed a geometric analysis of gender direction of the bias contained in the data. Using this property with the generation of gender-neutral analogies, a methodology was provided for modifying an embedding to remove gender stereotypes. Some metrics were defined to quantify both direct and indirect gender biases in embeddings and to develop algorithms to reduce bias in some embedding. Hence, the authors show that embeddings can be used in applications without amplifying gender bias.

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `13`
- text: where $v_i$ is the $i$-th event, $R_i$ is the reference score of $v_i$, and $N_{\rm ACP}$ is the number of the events of the ACP Corpus. To optimize the hyperparameters, we used the dev set of the ACP Corpus. For the evaluation, we used the test set of the ACP Corpus. The model output was classified as positive if $p(x) > 0$ and negative if $p(x) \le 0$.

- section: `Experiments ::: Model Configurations`
- segment_id: `14`
- text: As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states. BERT BIBREF17 is a pre-trained multi-layer bidirectional Transformer BIBREF18 encoder. Its output is the final hidden state corresponding to the special classification tag ([CLS]). For the details of ${\rm Encoder}$, see Sections SECREF30. We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.

- section: `Crowdsourcing Annotation ::: Comparing Experts with Crowds`
- segment_id: `25`
- text: Sadness is also the most frequent emotion, both according to experts and crowds. Other emotions for which a reasonable agreement is achieved are Annoyance, Awe/Sublime, Beauty/Joy, Humor ($\kappa $ > 0.2). Emotions with little agreement are Vitality, Uneasiness, Suspense, Nostalgia ($\kappa $ < 0.2). By and large, we note from Figure FIGREF18 that expert annotation is more restrictive, with experts agreeing more often on particular emotion labels (seen in the darker diagonal). The results of the crowdsourcing experiment, on the other hand, are a mixed bag as evidenced by a much sparser distribution of emotion labels. However, we note that these differences can be caused by 1) the disparate training procedure for the experts and crowds, and 2) the lack of opportunities for close supervision and on-going training of the crowds, as opposed to the in-house expert annotators. In general, however, we find that substituting experts with crowds is possible to a certain degree. Even though the crowds' labels look inconsistent at first view, there appears to be a good signal in their aggregated annotations, helping to approximate expert annotations to a certain degree. The average $\kappa $ agreement (with the experts) we get from $N=10$ crowd workers (0.24) is still considerably below the agreement among the experts (0.70).

- section: `Modeling`
- segment_id: `26`
- text: To estimate the difficulty of automatic classification of our data set, we perform multi-label document classification (of stanzas) with BERT BIBREF41. For this experiment we aggregate all labels for a stanza and sort them by frequency, both for the gold standard and the raw expert annotations. As can be seen in Figure FIGREF23, a stanza bears a minimum of one and a maximum of four emotions. Unfortunately, the label Nostalgia is only available 16 times in the German data (the gold standard) as a second label (as discussed in Section SECREF19). None of our models was able to learn this label for German. Therefore we omit it, leaving us with eight proper labels. We use the code and the pre-trained BERT models of Farm, provided by deepset.ai. We test the multilingual-uncased model (Multiling), the german-base-cased model (Base), the german-dbmdz-uncased model (Dbmdz), and we tune the Base model on 80k stanzas of the German Poetry Corpus DLK BIBREF30 for 2 epochs, both on token (masked words) and sequence (next line) prediction (Base$_{\textsc {Tuned}}$). We split the randomized German dataset so that each label is at least 10 times in the validation set (63 instances, 113 labels), and at least 10 times in the test set (56 instances, 108 labels) and leave the rest for training (617 instances, 946 labels).

- section: `Modeling`
- segment_id: `27`
- text: We train BERT for 10 epochs (with a batch size of 8), optimize with entropy loss, and report F1-micro on the test set. See Table TABREF36 for the results. We find that the multilingual model cannot handle infrequent categories, i.e., Awe/Sublime, Suspense and Humor. However, increasing the dataset with English data improves the results, suggesting that the classification would largely benefit from more annotated data. The best model overall is DBMDZ (.520), showing a balanced response on both validation and test set. See Table TABREF37 for a breakdown of all emotions as predicted by the this model. Precision is mostly higher than recall. The labels Awe/Sublime, Suspense and Humor are harder to predict than the other labels. The BASE and BASE$_{\textsc {TUNED}}$ models perform slightly worse than DBMDZ. The effect of tuning of the BASE model is questionable, probably because of the restricted vocabulary (30k). We found that tuning on poetry does not show obvious improvements. Lastly, we find that models that were trained on lines (instead of stanzas) do not achieve the same F1 (~.42 for the German models).

- section: `Concluding Remarks`
- segment_id: `29`
- text: For future work, we thus propose to repeat the experiment with larger number of crowdworkers, and develop an improved training strategy that would suit the crowdsourcing environment. The dataset presented in this paper can be of use for different application scenarios, including multi-label emotion classification, style-conditioned poetry generation, investigating the influence of rhythm/prosodic features on emotion, or analysis of authors, genres and diachronic variation (e.g., how emotions are represented differently in certain periods). Further, though our modeling experiments are still rudimentary, we propose that this data set can be used to investigate the intra-poem relations either through multi-task learning BIBREF49 and/or with the help of hierarchical sequence classification approaches.

- section: `Acknowledgements`
- segment_id: `30`
- text: A special thanks goes to Gesine Fuhrmann, who created the guidelines and tirelessly documented the annotation progress. Also thanks to Annika Palm and Debby Trzeciak who annotated and gave lively feedback. For help with the conceptualization of labels we thank Ines Schindler. This research has been partially conducted within the CRETA center (http://www.creta.uni-stuttgart.de/) which is funded by the German Ministry for Education and Research (BMBF) and partially funded by the German Research Council (DFG), projects SEAT (Structured Multi-Domain Emotion Analysis from Text, KL 2869/1-1). This work has also been supported by the German Research Foundation as part of the Research Training Group Adaptive Preparation of Information from Heterogeneous Sources (AIPHES) at the Technische Universität Darmstadt under grant No. GRK 1994/1.

- section: `Appendix`
- segment_id: `31`
- text: We illustrate two examples of our German gold standard annotation, a poem each by Friedrich Hölderlin and Georg Trakl, and an English poem by Walt Whitman. Hölderlin's text stands out, because the mood changes starkly from the first stanza to the second, from Beauty/Joy to Sadness. Trakl's text is a bit more complex with bits of Nostalgia and, most importantly, a mixture of Uneasiness with Awe/Sublime. Whitman's poem is an example of Vitality and its mixing with Sadness. The English annotation was unified by us for space constraints. For the full annotation please see https://github.com/tnhaider/poetry-emotion/

### Bridge
- section: `Introduction`
- segment_id: `1`
- text: This work aims to analyze and remove gender stereotypes from word embedding in Portuguese, analogous to what was done in BIBREF3 for the English language. Hence, we propose to employ a public word2vec model pre-trained to analyze gender bias in the Portuguese language, quantifying biases present in the model so that it is possible to reduce the spreading of sexism of such models. There is also a stage of bias reducing over the results obtained in the model, where it is sought to analyze the effects of the application of gender distinction reduction techniques. This paper is organized as follows: Section SECREF2 discusses related works. Section SECREF3 presents the Portuguese word2vec embeddings model used in this paper and Section SECREF4 proposes our method. Section SECREF5 presents experimental results, whose purpose is to verify results of a de-bias algorithm application in Portuguese embeddings word2vec model and a short discussion about it. Section SECREF6 brings our concluding remarks.
- bridge_detail: seed=`2`, total=`1.045`, adjacency=`1.000`, entity_overlap=`0.045`, section_continuity=`0.000`

- section: `Related Work`
- segment_id: `2`
- text: There is a wide range of techniques that provide interesting results in the context of ML algorithms geared to the classification of data without discrimination; these techniques range from the pre-processing of data BIBREF4 to the use of bias removal techniques BIBREF5 in fact. Approaches linked to the data pre-processing step usually consist of methods based on improving the quality of the dataset after which the usual classification tools can be used to train a classifier. So, it starts from a baseline already stipulated by the execution of itself. On the other side of the spectrum, there are Unsupervised and semi-supervised learning techniques, that are attractive because they do not imply the cost of corpus annotation BIBREF6 , BIBREF7 , BIBREF8 , BIBREF9 . The bias reduction is studied as a way to reduce discrimination through classification through different approaches BIBREF10 BIBREF11 . In BIBREF12 the authors propose to specify, implement, and evaluate the “fairness-aware" ML interface called themis-ml. In this interface, the main idea is to pick up a data set from a modified dataset.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Related Work`
- segment_id: `3`
- text: Themis-ml implements two methods for training fairness-aware models. The tool relies on two methods to make agnostic model type predictions: Reject Option Classification and Discrimination-Aware Ensemble Classification, these procedures being used to post-process predictions in a way that reduces potentially discriminatory predictions. According to the authors, it is possible to perceive the potential use of the method as a means of reducing bias in the use of ML algorithms. In BIBREF3 , the authors propose a method to hardly reduce bias in English word embeddings collected from Google News. Using word2vec, they performed a geometric analysis of gender direction of the bias contained in the data. Using this property with the generation of gender-neutral analogies, a methodology was provided for modifying an embedding to remove gender stereotypes. Some metrics were defined to quantify both direct and indirect gender biases in embeddings and to develop algorithms to reduce bias in some embedding. Hence, the authors show that embeddings can be used in applications without amplifying gender bias.
- bridge_detail: seed=`2`, total=`2.045`, adjacency=`1.000`, entity_overlap=`0.045`, section_continuity=`1.000`

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
- bridge_detail: seed=`12`, total=`1.071`, adjacency=`1.000`, entity_overlap=`0.071`, section_continuity=`0.000`

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:
- bridge_detail: seed segment or not added via bridge scoring

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `13`
- text: where $v_i$ is the $i$-th event, $R_i$ is the reference score of $v_i$, and $N_{\rm ACP}$ is the number of the events of the ACP Corpus. To optimize the hyperparameters, we used the dev set of the ACP Corpus. For the evaluation, we used the test set of the ACP Corpus. The model output was classified as positive if $p(x) > 0$ and negative if $p(x) \le 0$.
- bridge_detail: seed=`12`, total=`2.273`, adjacency=`1.000`, entity_overlap=`0.273`, section_continuity=`1.000`

- section: `Experiments ::: Model Configurations`
- segment_id: `14`
- text: As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states. BERT BIBREF17 is a pre-trained multi-layer bidirectional Transformer BIBREF18 encoder. Its output is the final hidden state corresponding to the special classification tag ([CLS]). For the details of ${\rm Encoder}$, see Sections SECREF30. We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.
- bridge_detail: seed=`15`, total=`1.250`, adjacency=`1.000`, entity_overlap=`0.250`, section_continuity=`0.000`

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.
- bridge_detail: seed=`15`, total=`2.111`, adjacency=`1.000`, entity_overlap=`0.111`, section_continuity=`1.000`

- section: `Crowdsourcing Annotation ::: Comparing Experts with Crowds`
- segment_id: `25`
- text: Sadness is also the most frequent emotion, both according to experts and crowds. Other emotions for which a reasonable agreement is achieved are Annoyance, Awe/Sublime, Beauty/Joy, Humor ($\kappa $ > 0.2). Emotions with little agreement are Vitality, Uneasiness, Suspense, Nostalgia ($\kappa $ < 0.2). By and large, we note from Figure FIGREF18 that expert annotation is more restrictive, with experts agreeing more often on particular emotion labels (seen in the darker diagonal). The results of the crowdsourcing experiment, on the other hand, are a mixed bag as evidenced by a much sparser distribution of emotion labels. However, we note that these differences can be caused by 1) the disparate training procedure for the experts and crowds, and 2) the lack of opportunities for close supervision and on-going training of the crowds, as opposed to the in-house expert annotators. In general, however, we find that substituting experts with crowds is possible to a certain degree. Even though the crowds' labels look inconsistent at first view, there appears to be a good signal in their aggregated annotations, helping to approximate expert annotations to a certain degree. The average $\kappa $ agreement (with the experts) we get from $N=10$ crowd workers (0.24) is still considerably below the agreement among the experts (0.70).
- bridge_detail: seed=`26`, total=`1.031`, adjacency=`1.000`, entity_overlap=`0.031`, section_continuity=`0.000`

- section: `Modeling`
- segment_id: `26`
- text: To estimate the difficulty of automatic classification of our data set, we perform multi-label document classification (of stanzas) with BERT BIBREF41. For this experiment we aggregate all labels for a stanza and sort them by frequency, both for the gold standard and the raw expert annotations. As can be seen in Figure FIGREF23, a stanza bears a minimum of one and a maximum of four emotions. Unfortunately, the label Nostalgia is only available 16 times in the German data (the gold standard) as a second label (as discussed in Section SECREF19). None of our models was able to learn this label for German. Therefore we omit it, leaving us with eight proper labels. We use the code and the pre-trained BERT models of Farm, provided by deepset.ai. We test the multilingual-uncased model (Multiling), the german-base-cased model (Base), the german-dbmdz-uncased model (Dbmdz), and we tune the Base model on 80k stanzas of the German Poetry Corpus DLK BIBREF30 for 2 epochs, both on token (masked words) and sequence (next line) prediction (Base$_{\textsc {Tuned}}$). We split the randomized German dataset so that each label is at least 10 times in the validation set (63 instances, 113 labels), and at least 10 times in the test set (56 instances, 108 labels) and leave the rest for training (617 instances, 946 labels).
- bridge_detail: seed segment or not added via bridge scoring

- section: `Modeling`
- segment_id: `27`
- text: We train BERT for 10 epochs (with a batch size of 8), optimize with entropy loss, and report F1-micro on the test set. See Table TABREF36 for the results. We find that the multilingual model cannot handle infrequent categories, i.e., Awe/Sublime, Suspense and Humor. However, increasing the dataset with English data improves the results, suggesting that the classification would largely benefit from more annotated data. The best model overall is DBMDZ (.520), showing a balanced response on both validation and test set. See Table TABREF37 for a breakdown of all emotions as predicted by the this model. Precision is mostly higher than recall. The labels Awe/Sublime, Suspense and Humor are harder to predict than the other labels. The BASE and BASE$_{\textsc {TUNED}}$ models perform slightly worse than DBMDZ. The effect of tuning of the BASE model is questionable, probably because of the restricted vocabulary (30k). We found that tuning on poetry does not show obvious improvements. Lastly, we find that models that were trained on lines (instead of stanzas) do not achieve the same F1 (~.42 for the German models).
- bridge_detail: seed=`26`, total=`2.172`, adjacency=`1.000`, entity_overlap=`0.172`, section_continuity=`1.000`

- section: `Concluding Remarks`
- segment_id: `29`
- text: For future work, we thus propose to repeat the experiment with larger number of crowdworkers, and develop an improved training strategy that would suit the crowdsourcing environment. The dataset presented in this paper can be of use for different application scenarios, including multi-label emotion classification, style-conditioned poetry generation, investigating the influence of rhythm/prosodic features on emotion, or analysis of authors, genres and diachronic variation (e.g., how emotions are represented differently in certain periods). Further, though our modeling experiments are still rudimentary, we propose that this data set can be used to investigate the intra-poem relations either through multi-task learning BIBREF49 and/or with the help of hierarchical sequence classification approaches.
- bridge_detail: seed=`30`, total=`1.036`, adjacency=`1.000`, entity_overlap=`0.036`, section_continuity=`0.000`

- section: `Acknowledgements`
- segment_id: `30`
- text: A special thanks goes to Gesine Fuhrmann, who created the guidelines and tirelessly documented the annotation progress. Also thanks to Annika Palm and Debby Trzeciak who annotated and gave lively feedback. For help with the conceptualization of labels we thank Ines Schindler. This research has been partially conducted within the CRETA center (http://www.creta.uni-stuttgart.de/) which is funded by the German Ministry for Education and Research (BMBF) and partially funded by the German Research Council (DFG), projects SEAT (Structured Multi-Domain Emotion Analysis from Text, KL 2869/1-1). This work has also been supported by the German Research Foundation as part of the Research Training Group Adaptive Preparation of Information from Heterogeneous Sources (AIPHES) at the Technische Universität Darmstadt under grant No. GRK 1994/1.
- bridge_detail: seed segment or not added via bridge scoring

- section: `Appendix`
- segment_id: `31`
- text: We illustrate two examples of our German gold standard annotation, a poem each by Friedrich Hölderlin and Georg Trakl, and an English poem by Walt Whitman. Hölderlin's text stands out, because the mood changes starkly from the first stanza to the second, from Beauty/Joy to Sadness. Trakl's text is a bit more complex with bits of Nostalgia and, most importantly, a mixture of Uneasiness with Awe/Sublime. Whitman's poem is an example of Vitality and its mixing with Sadness. The English annotation was unified by us for space constraints. For the full annotation please see https://github.com/tnhaider/poetry-emotion/
- bridge_detail: seed=`30`, total=`1.024`, adjacency=`1.000`, entity_overlap=`0.024`, section_continuity=`0.000`

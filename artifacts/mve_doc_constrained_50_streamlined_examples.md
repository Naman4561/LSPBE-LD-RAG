# Streamlined Bridge Qualitative Examples

Current-section streamlined config: `bridge_v21_streamlined_current|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15`
Improved-section streamlined config: `bridge_v21_streamlined_improved|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=improved|diversify=0:0.15`
No-section streamlined config: `bridge_v21_streamlined_none|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=none|diversify=0:0.15`
Best streamlined config: `bridge_v21_hybrid_soft|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=0:0.15`
Diversified comparison config: `bridge_v21_streamlined_current_diverse|method=bridge_v21_streamlined|k=10|seed_mode=hybrid|dense_w=1.00|sparse_w=0.50|section=current|diversify=1:0.15`

## Improved Section Helps

No example found for this category.

## No-Section Helps

No example found for this category.

## Current and Improved Tie

- paper_id: `1909.00694`
- question: What is the seed lexicon?
- gold evidence:
  - The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.

### Current Section
- section_mode: `current`
- section: `Introduction`
- segment_id: `0`
- text: Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive). Learning affective events is challenging because, as the examples above suggest, the polarity of an event is not necessarily predictable from its constituent words. Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowledge, which can hardly be learned from small annotated data. In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive).
- score_detail: seed or adjacency segment

- section: `Introduction`
- segment_id: `1`
- text: Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japanese web corpus. Given the minimum amount of supervision, they performed well. In addition, the combination of annotated and unannotated data yielded a gain over a purely supervised baseline when labeled data were small.
- score_detail: seed or adjacency segment

- section: `Related Work`
- segment_id: `2`
- text: Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movies), we work on how people are typically affected by events. In sentiment analysis, much attention has been paid to compositionality. Word-level polarity BIBREF5, BIBREF6, BIBREF7 and the roles of negation and intensification BIBREF8, BIBREF6, BIBREF9 are among the most important topics. In contrast, we are more interested in recognizing the sentiment polarity of an event that pertains to commonsense knowledge (e.g., getting money and catching cold). Label propagation from seed instances is a common approach to inducing sentiment polarities. While BIBREF5 and BIBREF10 worked on word- and phrase-level polarities, BIBREF0 dealt with event-level polarities. BIBREF5 and BIBREF10 linked instances using co-occurrence information and/or phrase-level coordinations (e.g., “$A$ and $B$” and “$A$ but $B$”).
- score_detail: seed or adjacency segment

- section: `Related Work`
- segment_id: `3`
- text: We shift our scope to event pairs that are more complex than phrase pairs, and consequently exploit discourse connectives as event-level counterparts of phrase-level conjunctions. BIBREF0 constructed a network of events using word embedding-derived similarities. Compared with this method, our discourse relation-based linking of events is much simpler and more intuitive. Some previous studies made use of document structure to understand the sentiment. BIBREF11 proposed a sentiment-specific pre-training strategy using unlabeled dialog data (tweet-reply pairs). BIBREF12 proposed a method of building a polarity-tagged corpus (ACP Corpus). They automatically gathered sentences that had positive or negative opinions utilizing HTML layout structures in addition to linguistic patterns. Our method depends only on raw texts and thus has wider applicability.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: AL (Automatically Labeled Pairs)`
- segment_id: `6`
- text: The seed lexicon matches (1) the latter event but (2) not the former event, and (3) their discourse relation type is Cause or Concession. If the discourse relation type is Cause, the former event is given the same score as the latter. Likewise, if the discourse relation type is Concession, the former event is given the opposite of the latter's score. They are used as reference scores during training.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Loss Functions`
- segment_id: `9`
- text: Using AL, CA, and CO data, we optimize the parameters of the polarity function $p(x)$. We define a loss function for each of the three types of event pairs and sum up the multiple loss functions. We use mean squared error to construct loss functions. For the AL data, the loss function is defined as: where $x_{i1}$ and $x_{i2}$ are the $i$-th pair of the AL data. $r_{i1}$ and $r_{i2}$ are the automatically-assigned scores of $x_{i1}$ and $x_{i2}$, respectively. $N_{\rm AL}$ is the total number of AL pairs, and $\lambda _{\rm AL}$ is a hyperparameter. For the CA data, the loss function is defined as: $y_{i1}$ and $y_{i2}$ are the $i$-th pair of the CA pairs. $N_{\rm CA}$ is the total number of CA pairs. $\lambda _{\rm CA}$ and $\mu $ are hyperparameters. The first term makes the scores of the two events closer while the second term prevents the scores from shrinking to zero. The loss function for the CO data is defined analogously: The difference is that the first term makes the scores of the two events distant from each other.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `10`
- text: As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction. . 重大な失敗を犯したので、仕事をクビになった。 Because [I] made a serious mistake, [I] got fired.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `13`
- text: where $v_i$ is the $i$-th event, $R_i$ is the reference score of $v_i$, and $N_{\rm ACP}$ is the number of the events of the ACP Corpus. To optimize the hyperparameters, we used the dev set of the ACP Corpus. For the evaluation, we used the test set of the ACP Corpus. The model output was classified as positive if $p(x) > 0$ and negative if $p(x) \le 0$.
- score_detail: seed=`11`, bridge=`1.097`, query=`0.518`, continuity=`0.079`, section=`1.000`, distance=`2`

- section: `Experiments ::: Model Configurations`
- segment_id: `14`
- text: As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states. BERT BIBREF17 is a pre-trained multi-layer bidirectional Transformer BIBREF18 encoder. Its output is the final hidden state corresponding to the special classification tag ([CLS]). For the details of ${\rm Encoder}$, see Sections SECREF30. We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.
- score_detail: seed or adjacency segment

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.
- score_detail: seed or adjacency segment

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.
- score_detail: seed or adjacency segment

- section: `Appendices ::: Seed Lexicon ::: Positive Words`
- segment_id: `19`
- text: 喜ぶ (rejoice), 嬉しい (be glad), 楽しい (be pleasant), 幸せ (be happy), 感動 (be impressed), 興奮 (be excited), 懐かしい (feel nostalgic), 好き (like), 尊敬 (respect), 安心 (be relieved), 感心 (admire), 落ち着く (be calm), 満足 (be satisfied), 癒される (be healed), and スッキリ (be refreshed).
- score_detail: seed=`17`, bridge=`0.502`, query=`0.502`, continuity=`0.000`, section=`0.000`, distance=`2`

### Improved Section
- section_mode: `improved`
- section: `Introduction`
- segment_id: `0`
- text: Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive). Learning affective events is challenging because, as the examples above suggest, the polarity of an event is not necessarily predictable from its constituent words. Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowledge, which can hardly be learned from small annotated data. In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive).
- score_detail: seed or adjacency segment

- section: `Introduction`
- segment_id: `1`
- text: Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japanese web corpus. Given the minimum amount of supervision, they performed well. In addition, the combination of annotated and unannotated data yielded a gain over a purely supervised baseline when labeled data were small.
- score_detail: seed or adjacency segment

- section: `Related Work`
- segment_id: `2`
- text: Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movies), we work on how people are typically affected by events. In sentiment analysis, much attention has been paid to compositionality. Word-level polarity BIBREF5, BIBREF6, BIBREF7 and the roles of negation and intensification BIBREF8, BIBREF6, BIBREF9 are among the most important topics. In contrast, we are more interested in recognizing the sentiment polarity of an event that pertains to commonsense knowledge (e.g., getting money and catching cold). Label propagation from seed instances is a common approach to inducing sentiment polarities. While BIBREF5 and BIBREF10 worked on word- and phrase-level polarities, BIBREF0 dealt with event-level polarities. BIBREF5 and BIBREF10 linked instances using co-occurrence information and/or phrase-level coordinations (e.g., “$A$ and $B$” and “$A$ but $B$”).
- score_detail: seed or adjacency segment

- section: `Related Work`
- segment_id: `3`
- text: We shift our scope to event pairs that are more complex than phrase pairs, and consequently exploit discourse connectives as event-level counterparts of phrase-level conjunctions. BIBREF0 constructed a network of events using word embedding-derived similarities. Compared with this method, our discourse relation-based linking of events is much simpler and more intuitive. Some previous studies made use of document structure to understand the sentiment. BIBREF11 proposed a sentiment-specific pre-training strategy using unlabeled dialog data (tweet-reply pairs). BIBREF12 proposed a method of building a polarity-tagged corpus (ACP Corpus). They automatically gathered sentences that had positive or negative opinions utilizing HTML layout structures in addition to linguistic patterns. Our method depends only on raw texts and thus has wider applicability.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: AL (Automatically Labeled Pairs)`
- segment_id: `6`
- text: The seed lexicon matches (1) the latter event but (2) not the former event, and (3) their discourse relation type is Cause or Concession. If the discourse relation type is Cause, the former event is given the same score as the latter. Likewise, if the discourse relation type is Concession, the former event is given the opposite of the latter's score. They are used as reference scores during training.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Loss Functions`
- segment_id: `9`
- text: Using AL, CA, and CO data, we optimize the parameters of the polarity function $p(x)$. We define a loss function for each of the three types of event pairs and sum up the multiple loss functions. We use mean squared error to construct loss functions. For the AL data, the loss function is defined as: where $x_{i1}$ and $x_{i2}$ are the $i$-th pair of the AL data. $r_{i1}$ and $r_{i2}$ are the automatically-assigned scores of $x_{i1}$ and $x_{i2}$, respectively. $N_{\rm AL}$ is the total number of AL pairs, and $\lambda _{\rm AL}$ is a hyperparameter. For the CA data, the loss function is defined as: $y_{i1}$ and $y_{i2}$ are the $i$-th pair of the CA pairs. $N_{\rm CA}$ is the total number of CA pairs. $\lambda _{\rm CA}$ and $\mu $ are hyperparameters. The first term makes the scores of the two events closer while the second term prevents the scores from shrinking to zero. The loss function for the CO data is defined analogously: The difference is that the first term makes the scores of the two events distant from each other.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `10`
- text: As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction. . 重大な失敗を犯したので、仕事をクビになった。 Because [I] made a serious mistake, [I] got fired.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `13`
- text: where $v_i$ is the $i$-th event, $R_i$ is the reference score of $v_i$, and $N_{\rm ACP}$ is the number of the events of the ACP Corpus. To optimize the hyperparameters, we used the dev set of the ACP Corpus. For the evaluation, we used the test set of the ACP Corpus. The model output was classified as positive if $p(x) > 0$ and negative if $p(x) \le 0$.
- score_detail: seed=`11`, bridge=`1.222`, query=`0.518`, continuity=`0.079`, section=`1.250`, distance=`2`

- section: `Experiments ::: Model Configurations`
- segment_id: `14`
- text: As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states. BERT BIBREF17 is a pre-trained multi-layer bidirectional Transformer BIBREF18 encoder. Its output is the final hidden state corresponding to the special classification tag ([CLS]). For the details of ${\rm Encoder}$, see Sections SECREF30. We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.
- score_detail: seed or adjacency segment

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.
- score_detail: seed or adjacency segment

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.
- score_detail: seed or adjacency segment

- section: `Appendices ::: Seed Lexicon ::: Positive Words`
- segment_id: `19`
- text: 喜ぶ (rejoice), 嬉しい (be glad), 楽しい (be pleasant), 幸せ (be happy), 感動 (be impressed), 興奮 (be excited), 懐かしい (feel nostalgic), 好き (like), 尊敬 (respect), 安心 (be relieved), 感心 (admire), 落ち着く (be calm), 満足 (be satisfied), 癒される (be healed), and スッキリ (be refreshed).
- score_detail: seed=`17`, bridge=`0.502`, query=`0.502`, continuity=`0.000`, section=`0.000`, distance=`2`


## Diversification Helps

No example found for this category.

## Failure Case

- paper_id: `1909.00694`
- question: How big are improvements of supervszed learning results trained on smalled labeled data enhanced with proposed approach copared to basic approach?
- gold evidence:
  - FLOAT SELECTED: Table 4: Results for small labeled training data. Given the performance with the full dataset, we show BERT trained only with the AL data.

### Current Bridge v2 Baseline
- section_mode: `n/a`
- section: `Proposed Method ::: Polarity Function`
- segment_id: `4`
- text: Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with the following form: ${\rm Encoder}$ outputs a vector representation of the event $x$. ${\rm Linear}$ is a fully-connected layer and transforms the representation into a scalar. ${\rm tanh}$ is the hyperbolic tangent and transforms the scalar into a score ranging from $-1$ to 1. In Section SECREF21, we consider two specific implementations of ${\rm Encoder}$.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs`
- segment_id: `5`
- text: Our method requires a very small seed lexicon and a large raw corpus. We assume that we can automatically extract discourse-tagged event pairs, $(x_{i1}, x_{i2})$ ($i=1, \cdots $) from the raw corpus. We refer to $x_{i1}$ and $x_{i2}$ as former and latter events, respectively. As shown in Figure FIGREF1, we limit our scope to two discourse relations: Cause and Concession. The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: AL (Automatically Labeled Pairs)`
- segment_id: `6`
- text: The seed lexicon matches (1) the latter event but (2) not the former event, and (3) their discourse relation type is Cause or Concession. If the discourse relation type is Cause, the former event is given the same score as the latter. Likewise, if the discourse relation type is Concession, the former event is given the opposite of the latter's score. They are used as reference scores during training.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.
- score_detail: bridge detail available

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Loss Functions`
- segment_id: `9`
- text: Using AL, CA, and CO data, we optimize the parameters of the polarity function $p(x)$. We define a loss function for each of the three types of event pairs and sum up the multiple loss functions. We use mean squared error to construct loss functions. For the AL data, the loss function is defined as: where $x_{i1}$ and $x_{i2}$ are the $i$-th pair of the AL data. $r_{i1}$ and $r_{i2}$ are the automatically-assigned scores of $x_{i1}$ and $x_{i2}$, respectively. $N_{\rm AL}$ is the total number of AL pairs, and $\lambda _{\rm AL}$ is a hyperparameter. For the CA data, the loss function is defined as: $y_{i1}$ and $y_{i2}$ are the $i$-th pair of the CA pairs. $N_{\rm CA}$ is the total number of CA pairs. $\lambda _{\rm CA}$ and $\mu $ are hyperparameters. The first term makes the scores of the two events closer while the second term prevents the scores from shrinking to zero. The loss function for the CO data is defined analogously: The difference is that the first term makes the scores of the two events distant from each other.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `10`
- text: As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction. . 重大な失敗を犯したので、仕事をクビになった。 Because [I] made a serious mistake, [I] got fired.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `13`
- text: where $v_i$ is the $i$-th event, $R_i$ is the reference score of $v_i$, and $N_{\rm ACP}$ is the number of the events of the ACP Corpus. To optimize the hyperparameters, we used the dev set of the ACP Corpus. For the evaluation, we used the test set of the ACP Corpus. The model output was classified as positive if $p(x) > 0$ and negative if $p(x) \le 0$.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Model Configurations`
- segment_id: `14`
- text: As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states. BERT BIBREF17 is a pre-trained multi-layer bidirectional Transformer BIBREF18 encoder. Its output is the final hidden state corresponding to the special classification tag ([CLS]). For the details of ${\rm Encoder}$, see Sections SECREF30. We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.
- score_detail: seed or adjacency segment

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.
- score_detail: seed or adjacency segment

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.
- score_detail: seed or adjacency segment

- section: `Appendices ::: Seed Lexicon ::: Positive Words`
- segment_id: `19`
- text: 喜ぶ (rejoice), 嬉しい (be glad), 楽しい (be pleasant), 幸せ (be happy), 感動 (be impressed), 興奮 (be excited), 懐かしい (feel nostalgic), 好き (like), 尊敬 (respect), 安心 (be relieved), 感心 (admire), 落ち着く (be calm), 満足 (be satisfied), 癒される (be healed), and スッキリ (be refreshed).
- score_detail: seed or adjacency segment

- section: `Appendices ::: Seed Lexicon ::: Negative Words`
- segment_id: `20`
- text: 怒る (get angry), 悲しい (be sad), 寂しい (be lonely), 怖い (be scared), 不安 (feel anxious), 恥ずかしい (be embarrassed), 嫌 (hate), 落ち込む (feel down), 退屈 (be bored), 絶望 (feel hopeless), 辛い (have a hard time), 困る (have trouble), 憂鬱 (be depressed), 心配 (be worried), and 情けない (be sorry).
- score_detail: seed or adjacency segment

- section: `Appendices ::: Settings of Encoder ::: BiGRU`
- segment_id: `21`
- text: The dimension of the embedding layer was 256. The embedding layer was initialized with the word embeddings pretrained using the Web corpus. The input sentences were segmented into words by the morphological analyzer Juman++. The vocabulary size was 100,000. The number of hidden layers was 2. The dimension of hidden units was 256. The optimizer was Momentum SGD BIBREF21. The mini-batch size was 1024. We ran 100 epochs and selected the snapshot that achieved the highest score for the dev set.
- score_detail: seed or adjacency segment

- section: `Appendices ::: Settings of Encoder ::: BERT`
- segment_id: `22`
- text: We used a Japanese BERT model pretrained with Japanese Wikipedia. The input sentences were segmented into words by Juman++, and words were broken into subwords by applying BPE BIBREF20. The vocabulary size was 32,000. The maximum length of an input sequence was 128. The number of hidden layers was 12. The dimension of hidden units was 768. The number of self-attention heads was 12. The optimizer was Adam BIBREF19. The mini-batch size was 32. We ran 1 epoch.
- score_detail: seed or adjacency segment

### Best Streamlined
- section_mode: `current`
- section: `Introduction`
- segment_id: `0`
- text: Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positive to the experiencers; catching cold and losing one's wallet are negative. Understanding affective events is important to various natural language processing (NLP) applications such as dialogue systems BIBREF1, question-answering systems BIBREF2, and humor recognition BIBREF3. In this paper, we work on recognizing the polarity of an affective event that is represented by a score ranging from $-1$ (negative) to 1 (positive). Learning affective events is challenging because, as the examples above suggest, the polarity of an event is not necessarily predictable from its constituent words. Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowledge, which can hardly be learned from small annotated data. In this paper, we propose a simple and effective method for learning affective events that only requires a very small seed lexicon and a large raw corpus. As illustrated in Figure FIGREF1, our key idea is that we can exploit discourse relations BIBREF4 to efficiently propagate polarity from seed predicates that directly report one's emotions (e.g., “to be glad” is positive).
- score_detail: seed or adjacency segment

- section: `Introduction`
- segment_id: `1`
- text: Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be negative indicates the negative polarity of $x_1$. Similarly, if $x_1$ and $x_2$ are in the discourse relation of Concession (i.e., $x_2$ in spite of $x_1$), the reverse of $x_2$'s polarity can be propagated to $x_1$. Even if $x_2$'s polarity is not known in advance, we can exploit the tendency of $x_1$ and $x_2$ to be of the same polarity (for Cause) or of the reverse polarity (for Concession) although the heuristic is not exempt from counterexamples. We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japanese web corpus. Given the minimum amount of supervision, they performed well. In addition, the combination of annotated and unannotated data yielded a gain over a purely supervised baseline when labeled data were small.
- score_detail: seed or adjacency segment

- section: `Related Work`
- segment_id: `2`
- text: Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movies), we work on how people are typically affected by events. In sentiment analysis, much attention has been paid to compositionality. Word-level polarity BIBREF5, BIBREF6, BIBREF7 and the roles of negation and intensification BIBREF8, BIBREF6, BIBREF9 are among the most important topics. In contrast, we are more interested in recognizing the sentiment polarity of an event that pertains to commonsense knowledge (e.g., getting money and catching cold). Label propagation from seed instances is a common approach to inducing sentiment polarities. While BIBREF5 and BIBREF10 worked on word- and phrase-level polarities, BIBREF0 dealt with event-level polarities. BIBREF5 and BIBREF10 linked instances using co-occurrence information and/or phrase-level coordinations (e.g., “$A$ and $B$” and “$A$ but $B$”).
- score_detail: seed or adjacency segment

- section: `Related Work`
- segment_id: `3`
- text: We shift our scope to event pairs that are more complex than phrase pairs, and consequently exploit discourse connectives as event-level counterparts of phrase-level conjunctions. BIBREF0 constructed a network of events using word embedding-derived similarities. Compared with this method, our discourse relation-based linking of events is much simpler and more intuitive. Some previous studies made use of document structure to understand the sentiment. BIBREF11 proposed a sentiment-specific pre-training strategy using unlabeled dialog data (tweet-reply pairs). BIBREF12 proposed a method of building a polarity-tagged corpus (ACP Corpus). They automatically gathered sentences that had positive or negative opinions utilizing HTML layout structures in addition to linguistic patterns. Our method depends only on raw texts and thus has wider applicability.
- score_detail: seed=`1`, bridge=`0.648`, query=`0.578`, continuity=`0.070`, section=`0.000`, distance=`2`

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CA (Cause Pairs)`
- segment_id: `7`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Cause. We assume the two events have the same polarities.
- score_detail: seed=`9`, bridge=`1.021`, query=`0.480`, continuity=`0.041`, section=`1.000`, distance=`2`

- section: `Proposed Method ::: Discourse Relation-Based Event Pairs ::: CO (Concession Pairs)`
- segment_id: `8`
- text: The seed lexicon matches neither the former nor the latter event, and their discourse relation type is Concession. We assume the two events have the reversed polarities.
- score_detail: seed or adjacency segment

- section: `Proposed Method ::: Loss Functions`
- segment_id: `9`
- text: Using AL, CA, and CO data, we optimize the parameters of the polarity function $p(x)$. We define a loss function for each of the three types of event pairs and sum up the multiple loss functions. We use mean squared error to construct loss functions. For the AL data, the loss function is defined as: where $x_{i1}$ and $x_{i2}$ are the $i$-th pair of the AL data. $r_{i1}$ and $r_{i2}$ are the automatically-assigned scores of $x_{i1}$ and $x_{i2}$, respectively. $N_{\rm AL}$ is the total number of AL pairs, and $\lambda _{\rm AL}$ is a hyperparameter. For the CA data, the loss function is defined as: $y_{i1}$ and $y_{i2}$ are the $i$-th pair of the CA pairs. $N_{\rm CA}$ is the total number of CA pairs. $\lambda _{\rm CA}$ and $\mu $ are hyperparameters. The first term makes the scores of the two events closer while the second term prevents the scores from shrinking to zero. The loss function for the CO data is defined analogously: The difference is that the first term makes the scores of the two events distant from each other.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `10`
- text: As a raw corpus, we used a Japanese web corpus that was compiled through the procedures proposed by BIBREF13. To extract event pairs tagged with discourse relations, we used the Japanese dependency parser KNP and in-house postprocessing scripts BIBREF14. KNP used hand-written rules to segment each sentence into what we conventionally called clauses (mostly consecutive text chunks), each of which contained one main predicate. KNP also identified the discourse relations of event pairs if explicit discourse connectives BIBREF4 such as “ので” (because) and “のに” (in spite of) were present. We treated Cause/Reason (原因・理由) and Condition (条件) in the original tagset BIBREF15 as Cause and Concession (逆接) as Concession, respectively. Here is an example of event pair extraction. . 重大な失敗を犯したので、仕事をクビになった。 Because [I] made a serious mistake, [I] got fired.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: AL, CA, and CO`
- segment_id: `11`
- text: From this sentence, we extracted the event pair of “重大な失敗を犯す” ([I] make a serious mistake) and “仕事をクビになる” ([I] get fired), and tagged it with Cause. We constructed our seed lexicon consisting of 15 positive words and 15 negative words, as shown in Section SECREF27. From the corpus of about 100 million sentences, we obtained 1.4 millions event pairs for AL, 41 millions for CA, and 6 millions for CO. We randomly selected subsets of AL event pairs such that positive and negative latter events were equal in size. We also sampled event pairs for each of CA and CO such that it was five times larger than AL. The results are shown in Table TABREF16.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `12`
- text: We used the latest version of the ACP Corpus BIBREF12 for evaluation. It was used for (semi-)supervised training as well. Extracted from Japanese websites using HTML layouts and linguistic patterns, the dataset covered various genres. For example, the following two sentences were labeled positive and negative, respectively: . 作業が楽だ。 The work is easy. . 駐車場がない。 There is no parking lot. Although the ACP corpus was originally constructed in the context of sentiment analysis, we found that it could roughly be regarded as a collection of affective events. We parsed each sentence and extracted the last clause in it. The train/dev/test split of the data is shown in Table TABREF19. The objective function for supervised training is:
- score_detail: seed or adjacency segment

- section: `Experiments ::: Dataset ::: ACP (ACP Corpus)`
- segment_id: `13`
- text: where $v_i$ is the $i$-th event, $R_i$ is the reference score of $v_i$, and $N_{\rm ACP}$ is the number of the events of the ACP Corpus. To optimize the hyperparameters, we used the dev set of the ACP Corpus. For the evaluation, we used the test set of the ACP Corpus. The model output was classified as positive if $p(x) > 0$ and negative if $p(x) \le 0$.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Model Configurations`
- segment_id: `14`
- text: As for ${\rm Encoder}$, we compared two types of neural networks: BiGRU and BERT. GRU BIBREF16 is a recurrent neural network sequence encoder. BiGRU reads an input sequence forward and backward and the output is the concatenation of the final forward and backward hidden states. BERT BIBREF17 is a pre-trained multi-layer bidirectional Transformer BIBREF18 encoder. Its output is the final hidden state corresponding to the special classification tag ([CLS]). For the details of ${\rm Encoder}$, see Sections SECREF30. We trained the model with the following four combinations of the datasets: AL, AL+CA+CO (two proposed models), ACP (supervised), and ACP+AL+CA+CO (semi-supervised). The corresponding objective functions were: $\mathcal {L}_{\rm AL}$, $\mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$, $\mathcal {L}_{\rm ACP}$, and $\mathcal {L}_{\rm ACP} + \mathcal {L}_{\rm AL} + \mathcal {L}_{\rm CA} + \mathcal {L}_{\rm CO}$.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `15`
- text: Table TABREF23 shows accuracy. As the Random baseline suggests, positive and negative labels were distributed evenly. The Random+Seed baseline made use of the seed lexicon and output the corresponding label (or the reverse of it for negation) if the event's predicate is in the seed lexicon. We can see that the seed lexicon itself had practically no impact on prediction. The models in the top block performed considerably better than the random baselines. The performance gaps with their (semi-)supervised counterparts, shown in the middle block, were less than 7%. This demonstrates the effectiveness of discourse relation-based label propagation. Comparing the model variants, we obtained the highest score with the BiGRU encoder trained with the AL+CA+CO dataset. BERT was competitive but its performance went down if CA and CO were used in addition to AL. We conjecture that BERT was more sensitive to noises found more frequently in CA and CO. Contrary to our expectations, supervised models (ACP) outperformed semi-supervised models (ACP+AL+CA+CO). This suggests that the training set of 0.6 million events is sufficiently large for training the models. For comparison, we trained the models with a subset (6,000 events) of the ACP dataset. As the results shown in Table TABREF24 demonstrate, our method is effective when labeled data are small.
- score_detail: seed or adjacency segment

- section: `Experiments ::: Results and Discussion`
- segment_id: `16`
- text: The result of hyperparameter optimization for the BiGRU encoder was as follows: As the CA and CO pairs were equal in size (Table TABREF16), $\lambda _{\rm CA}$ and $\lambda _{\rm CO}$ were comparable values. $\lambda _{\rm CA}$ was about one-third of $\lambda _{\rm CO}$, and this indicated that the CA pairs were noisier than the CO pairs. A major type of CA pairs that violates our assumption was in the form of “$\textit {problem}_{\text{negative}}$ causes $\textit {solution}_{\text{positive}}$”: . (悪いところがある, よくなるように努力する) (there is a bad point, [I] try to improve [it]) The polarities of the two events were reversed in spite of the Cause relation, and this lowered the value of $\lambda _{\rm CA}$. Some examples of model outputs are shown in Table TABREF26. The first two examples suggest that our model successfully learned negation without explicit supervision. Similarly, the next two examples differ only in voice but the model correctly recognized that they had opposite polarities. The last two examples share the predicate “落とす" (drop) and only the objects are different. The second event “肩を落とす" (lit. drop one's shoulders) is an idiom that expresses a disappointed feeling. The examples demonstrate that our model correctly learned non-compositional expressions.
- score_detail: seed or adjacency segment

- section: `Conclusion`
- segment_id: `17`
- text: In this paper, we proposed to use discourse relations to effectively propagate polarities of affective events from seeds. Experiments show that, even with a minimal amount of supervision, the proposed method performed well. Although event pairs linked by discourse analysis are shown to be useful, they nevertheless contain noises. Adding linguistically-motivated filtering rules would help improve the performance.
- score_detail: seed or adjacency segment

- section: `Acknowledgments`
- segment_id: `18`
- text: We thank Nobuhiro Kaji for providing the ACP Corpus and Hirokazu Kiyomaru and Yudai Kishimoto for their help in extracting event pairs. This work was partially supported by Yahoo! Japan Corporation.
- score_detail: seed or adjacency segment

- section: `Appendices ::: Seed Lexicon ::: Positive Words`
- segment_id: `19`
- text: 喜ぶ (rejoice), 嬉しい (be glad), 楽しい (be pleasant), 幸せ (be happy), 感動 (be impressed), 興奮 (be excited), 懐かしい (feel nostalgic), 好き (like), 尊敬 (respect), 安心 (be relieved), 感心 (admire), 落ち着く (be calm), 満足 (be satisfied), 癒される (be healed), and スッキリ (be refreshed).
- score_detail: seed or adjacency segment

- section: `Appendices ::: Seed Lexicon ::: Negative Words`
- segment_id: `20`
- text: 怒る (get angry), 悲しい (be sad), 寂しい (be lonely), 怖い (be scared), 不安 (feel anxious), 恥ずかしい (be embarrassed), 嫌 (hate), 落ち込む (feel down), 退屈 (be bored), 絶望 (feel hopeless), 辛い (have a hard time), 困る (have trouble), 憂鬱 (be depressed), 心配 (be worried), and 情けない (be sorry).
- score_detail: seed or adjacency segment

- section: `Appendices ::: Settings of Encoder ::: BiGRU`
- segment_id: `21`
- text: The dimension of the embedding layer was 256. The embedding layer was initialized with the word embeddings pretrained using the Web corpus. The input sentences were segmented into words by the morphological analyzer Juman++. The vocabulary size was 100,000. The number of hidden layers was 2. The dimension of hidden units was 256. The optimizer was Momentum SGD BIBREF21. The mini-batch size was 1024. We ran 100 epochs and selected the snapshot that achieved the highest score for the dev set.
- score_detail: seed or adjacency segment

- section: `Appendices ::: Settings of Encoder ::: BERT`
- segment_id: `22`
- text: We used a Japanese BERT model pretrained with Japanese Wikipedia. The input sentences were segmented into words by Juman++, and words were broken into subwords by applying BPE BIBREF20. The vocabulary size was 32,000. The maximum length of an input sequence was 128. The number of hidden layers was 12. The dimension of hidden units was 768. The number of self-attention heads was 12. The optimizer was Adam BIBREF19. The mini-batch size was 32. We ran 1 epoch.
- score_detail: seed or adjacency segment

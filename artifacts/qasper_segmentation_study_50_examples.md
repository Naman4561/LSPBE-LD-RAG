# QASPER Segmentation Study Examples

## Paragraph Best

No example found for this category.

## Paragraph Pair Best

- paper_id: `1712.09127`
- question: Do they evaluate grammaticality of generated text?
- gold evidence:
  - We hypothesize that because weGAN takes into account document labels in a semi-supervised way, the embeddings trained from weGAN can better incorporate the labeling information and therefore, produce document embeddings which are better separated. The results are shown in Table 1 and averaged over 5 randomized runs. Performing the Welch's t-test, both changes after weGAN training are statistically significant at a INLINEFORM0 significance level. Because the Rand index captures matching accuracy, we observe from the Table 1 that weGAN tends to improve both metrics.

- `seg_paragraph`: hit=`0`, seed_distance=`5`
  - 0:Generative adversarial nets (GAN) (Goodfellow et al., 2014) belong to a class of generative models which are trainable and can generate artificial data examples
  - 3:(2016) proposed textGAN in which the generator has the following form, DISPLAYFORM0 where INLINEFORM0 is the noise vector, INLINEFORM1 is the generated sentence
  - 5:We assume that for each corpora INLINEFORM0 , we are given word embeddings for each word INLINEFORM1 , where INLINEFORM2 is the dimension of each word embedding
- `seg_paragraph_pair`: hit=`1`, seed_distance=`3`
  - 0:Generative adversarial nets (GAN) (Goodfellow et al., 2014) belong to a class of generative models which are trainable and can generate artificial data examples
  - 1:In a GAN model, we assume that the data examples INLINEFORM0 are drawn from a distribution INLINEFORM1 , and the artificial data examples INLINEFORM2 are transf
  - 2:Suppose we have a number of different corpora INLINEFORM0 , which for example can be based on different categories or sentiments of text documents. We suppose t
- `seg_micro_chunk`: hit=`0`, seed_distance=`10`
  - 1:The GAN model has been shown to closely replicate a number of image data sets, such as MNIST, Toronto Face Database (TFD), CIFAR-10, SVHN, and ImageNet (Goodfel
  - 2:Glover (2016) provided such a model with the energy-based GAN (Zhao et al., 2017). To the best of our knowledge, there has been no literature on applying the GA
  - 4:For the second problem, we train a GAN model which considers both cross-corpus and per-corpus “topics” in the generator, and applies a discriminator which consi

## Micro Chunk Best

No example found for this category.

## Tie Case

- paper_id: `1909.00694`
- question: What is the seed lexicon?
- gold evidence:
  - The seed lexicon consists of positive and negative predicates. If the predicate of an extracted event is in the seed lexicon and does not involve complex phenomena like negation, we assign the corresponding polarity score ($+1$ for positive events and $-1$ for negative events) to the event. We expect the model to automatically learn complex phenomena through label propagation. Based on the availability of scores and the types of discourse relations, we classify the extracted event pairs into the following three types.

- `seg_paragraph`: hit=`1`, seed_distance=`2`
  - 0:Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positiv
  - 1:Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is
  - 2:Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movi
- `seg_paragraph_pair`: hit=`1`, seed_distance=`2`
  - 0:Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positiv
  - 1:Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movi
  - 2:Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with t
- `seg_micro_chunk`: hit=`1`, seed_distance=`14`
  - 0:Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positiv
  - 1:Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowled
  - 2:If the seed lexicon suggests $x_2$ is positive, $x_1$ is also likely to be positive because it triggers the positive emotion. The fact that $x_2$ is known to be

## Failure Case

- paper_id: `1909.00694`
- question: How big are improvements of supervszed learning results trained on smalled labeled data enhanced with proposed approach copared to basic approach?
- gold evidence:
  - FLOAT SELECTED: Table 4: Results for small labeled training data. Given the performance with the full dataset, we show BERT trained only with the AL data.

- `seg_paragraph`: hit=`0`, seed_distance=`unknown`
  - 0:Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positiv
  - 1:Suppose that events $x_1$ are $x_2$ are in the discourse relation of Cause (i.e., $x_1$ causes $x_2$). If the seed lexicon suggests $x_2$ is positive, $x_1$ is
  - 2:Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movi
- `seg_paragraph_pair`: hit=`0`, seed_distance=`unknown`
  - 0:Affective events BIBREF0 are events that typically affect people in positive or negative ways. For example, getting money and playing sports are usually positiv
  - 1:Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movi
  - 2:Our goal is to learn the polarity function $p(x)$, which predicts the sentiment polarity score of an event $x$. We approximate $p(x)$ by a neural network with t
- `seg_micro_chunk`: hit=`0`, seed_distance=`unknown`
  - 1:Combined with the unbounded combinatorial nature of language, the non-compositionality of affective polarity entails the need for large amounts of world knowled
  - 3:We transform this idea into objective functions and train neural network models that predict the polarity of a given event. We trained the models using a Japane
  - 4:Learning affective events is closely related to sentiment analysis. Whereas sentiment analysis usually focuses on the polarity of what are described (e.g., movi

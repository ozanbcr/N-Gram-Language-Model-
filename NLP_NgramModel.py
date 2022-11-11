import re
import io
import pandas as pd

with io.open('hw01_tinytr.txt', 'r', encoding = "utf8") as f:
    text = f.read()

sentence_count = len(re.findall(r'[.!?]', text))
count_word = len(text.split())


token_list = re.findall(r"\w+(?:'\w+)?|[^\w\s]", text)
token_list = [i.lower() for i in token_list]

for i in range(len(token_list)):
    if token_list[i] in (".", "?", "!"):
        token_list[i] = "</s>"

end_sentence_index = []
for index, val in enumerate(token_list):
    if val == "</s>" :
        end_sentence_index.append(index)

begin_sentence_index = [0]
for n, val in enumerate(end_sentence_index):
    begin_sentence_index.append(val + 2 + n)

for i in begin_sentence_index:
    token_list.insert(i, "<s>")

token_list.pop(-1)

####### Unigram  ##########
new_text = " ".join(token_list)
words = new_text.split()

def word_count(text):
    counts = dict()
    for word in text:
        if word in counts:
            counts[word] += 1
        else :
            counts[word] = 1
    return counts

unigram_count = word_count(words)

df_uni = pd.DataFrame()
df_uni["unigrams"] = [key for key in unigram_count]
df_uni["frequency"] = [unigram_count[key] for key in unigram_count]
df_uni["probability"] = [unigram_count[key]/len(words) for key in unigram_count]
df_uni = df_uni.sort_values("frequency", ascending=False)

dfAsString_uni = df_uni.to_string(header=True, index=False)

with open('hw01_tinytr_Sonuc.txt', 'a') as f:
    f.write(f"\n\n\nMetindeki Cümle Sayısı : {sentence_count}\n")
    f.write(f"Metindeki Toplam Kelime Sayısı (Corpus Size) : {count_word}\n")
    f.write(f"Metindeki Unique Kelime Sayısı (Vocabulary Size) : {len(unigram_count.keys())}   (<s> ve </s> dahil edildi)\n"  )
    f.write(dfAsString_uni)


############## Bigram ####################
deneme_list_bigram = {}
for i in unigram_count:
    for k in unigram_count:
        deneme_list_bigram[(i,k)] = 0

def createBigram(texttt):
    global deneme_list_bigram
    for i in range(len(texttt)-1):
        deneme_list_bigram[(texttt[i], texttt[i+1])] += 1
    return deneme_list_bigram

bigram_count = createBigram(words)

def calcBigramProb(unigram_countt, bigram_countt):
    list_prob = {}
    for key in bigram_countt:
        word1 = key[0]
        word2 = key[1]
        list_prob[key] = (bigram_countt[key])/(unigram_countt[word1])
    return list_prob

bigram_prob = calcBigramProb(unigram_count, bigram_count)

df_bi = pd.DataFrame()
df_bi["bigram"] = [key for key in bigram_count]
df_bi["frequency"] = [bigram_count[key] for key in bigram_count]
df_bi["probability"] = [bigram_prob[key] for key in bigram_prob]

df_bi = df_bi.sort_values("frequency", ascending=False)[0:100]

dfAsString_bi = df_bi.to_string(header=True, index=False)


with open('hw01_tinytr_Sonuc.txt', 'a') as f:
    f.write(f"\n\n\nBigram Bilgileri :\n")
    f.write(dfAsString_bi)

########### UNK ve Smoothing #############
new_text_UNK = new_text.replace("dün", "UNK")
words_UNK = new_text_UNK.split()

unigram_count_UNK = word_count(words_UNK)

list_bigram_UNK = {}
for i in unigram_count_UNK:
    for k in unigram_count_UNK:
        list_bigram_UNK[(i,k)] = 0

def createBigram_UNK(texttt):
    global list_bigram_UNK
    for i in range(len(texttt)-1):
        list_bigram_UNK[(texttt[i], texttt[i+1])] += 1
    return list_bigram_UNK

bigram_count_UNK = createBigram_UNK(words_UNK)

def calcBigramProb_Smooth(unigram_countt, bigram_countt):
    list_prob = {}
    for key in bigram_countt:
        word1 = key[0]
        word2 = key[1]
        list_prob[key] = (bigram_countt[key] + 0.5)/((unigram_countt[word1] + len(unigram_countt.keys())*0.5))
    return list_prob

bigram_prob_UNK = calcBigramProb_Smooth(unigram_count_UNK, bigram_count_UNK)

df_UNK = pd.DataFrame()
df_UNK["bigram"] = [key for key in bigram_count_UNK]
df_UNK["probability"] = [bigram_prob[key] for key in bigram_prob]
df_UNK["smoothed_probability"] = [bigram_prob_UNK[key] for key in bigram_prob_UNK]

df_UNK = df_UNK.sort_values("smoothed_probability", ascending=False)[0:100]

dfAsString_UNK = df_UNK.to_string(header=True, index=False)

with open('hw01_tinytr_Sonuc.txt', 'a') as f:
    f.write(f"\n\n\nUNK değiştirme ve Smoothing sonrası :\n")
    f.write(dfAsString_UNK)

############ Calculating Sentence Prob #################

def sentenceProb(sentence):
    sentence = sentence.lower()
    word_sentence = sentence.split()
    prob = 1
    for j in range(len(word_sentence)- 1):
        if word_sentence[j] not in words_UNK:
            word_sentence[j] = "UNK"
        if word_sentence[j+1] not in words_UNK:
            word_sentence[j+1] = "UNK"
        prob = prob * bigram_prob_UNK[(word_sentence[j], word_sentence[j+1])]
    return prob



with open('hw01_tinytr_Sonuc.txt', 'a') as f:
    f.write(f"\n\n\n<s> Ali eve geldi </s>: {sentenceProb('<s> ali eve geldi </s>')}\n")
    f.write(f"\n<s> Mehmet eve ve okula Pazartesi gitti </s>: {sentenceProb('<s> Mehmet eve ve okula Pazartesi gitti </s>')}\n")




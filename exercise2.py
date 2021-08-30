import pandas as pd
import string

def splitDf(percentage_test, df):
    grouped = df.groupby(df.categoria)
    dfTest = pd.DataFrame()
    dfTrain = pd.DataFrame()
    for group in grouped.groups:
        dfTemp = grouped.get_group(group)
        dfTempTest = dfTemp.sample(frac=percentage_test)
        dfTest = pd.concat([dfTest, dfTempTest])
        dfTempTrain = dfTemp.drop(dfTempTest.index)
        dfTrain = pd.concat([dfTrain, dfTempTrain])
    return dfTest, dfTrain


def read_news(percentage_test):
    df = pd.read_excel("resources/ejercicio2.xlsx")
    df = df.loc[:, 'titular':'categoria']
    index_names = df[df['categoria'] == "Noticias destacadas"].index
    df.drop(index_names, inplace=True)
    index_names = df[df['categoria'] == "Destacadas"].index
    df.drop(index_names, inplace=True)
    df.dropna(subset = ["categoria"], inplace=True)
    dfTest, dfTrain = splitDf(percentage_test, df)
    dfTest.to_csv("testSample.csv", encoding='utf-8')
    dfTrain.to_csv("trainSample.csv", encoding='utf-8')
    return dfTest, dfTrain


def make_structures(df):
    dic = {}
    word_dic = {}

    for news in df.iterrows():
        if not news[1].categoria in dic:
            dic2 = {}
            dic[news[1].categoria] = dic2

        tokenized = normalize_and_tokenize_string(news[1].titular)

        for word in tokenized:
            if not word in word_dic:
                word_dic[word] = 1
            else:
                word_dic[word] += 1

            if not word in dic[news[1].categoria]:
                dic[news[1].categoria][word] = 1
            else:
                dic[news[1].categoria][word] += 1

    return dic, word_dic


def normalize_and_tokenize_string(s):
    for char in string.punctuation:
        s = s.replace(char, '')

    s = s.replace("¿", '')
    s = s.lower()
    return s.split(" ")


def category_probability(df):
    categories = df['categoria'].unique()
    dic = {}
    total = df['categoria'].count()
    for category in categories:
        dic[category] = (df[df["categoria"] == category].count())[0]/total

    return dic


def calculate_frequencies(category_dic, word_dic):
    for category in category_dic:
        for word in category_dic[category]:
            category_dic[category][word] = category_dic[category][word]/word_dic[word]


def laplace(val, total, k):
    return (val+1)/(total+k)


def classify(data, category_dic, word_dic, category_frecuency, categoria):
    category_probabilities = {}
    sum = 0

    for category in category_dic:
        category_probabilities[category] = 1

        for word in normalize_and_tokenize_string(data):
            if not word in category_dic[category]:
                if word in word_dic:
                    category_probabilities[category] *= laplace(0, word_dic[word], len(category_dic))
                else:
                    category_probabilities[category] *= (1/len(category_dic))
            else:
                category_probabilities[category] *= laplace(category_dic[category][word], word_dic[word], len(category_dic))

        category_probabilities[category] *= category_frecuency[category]
        sum += category_probabilities[category]

    print(category_probabilities, "\n", max(category_probabilities, key=category_probabilities.get), category_probabilities[categoria]/sum)
    if categoria == max(category_probabilities, key=category_probabilities.get):
        return True
    else:
        return False

def test_samples(dfTest, category_dic, word_dic, category_frecuency):
    hit = 0.0
    for index, row in dfTest.iterrows():
        if classify(row.titular, category_dic, word_dic, category_frecuency, row.categoria):
            hit += 1
    return hit/len(dfTest.index)

#dfTest, dfTrain = read_news(0.10)
df = pd.read_csv("test.csv")
dfTest = pd.read_csv("testSample.csv")
dfTrain = pd.read_csv("trainSample.csv")
dictionaries = make_structures(dfTrain)
calculate_frequencies(dictionaries[0], dictionaries[1])
hitPercentage = test_samples(dfTest, dictionaries[0], dictionaries[1], category_probability(df))
print("hit percentage", hitPercentage)
#classify("Ponsha juega al fútbol y ataja pelotas", dictionaries[0], dictionaries[1], category_probability(df))


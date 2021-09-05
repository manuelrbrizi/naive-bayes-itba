import pandas as pd
import string
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sn


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
    df.dropna(subset=["categoria"], inplace=True)
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
        dic[category] = (df[df["categoria"] == category].count())[0] / total

    return dic


def calculate_frequencies(category_dic, word_dic):
    for category in category_dic:
        for word in category_dic[category]:
            category_dic[category][word] = category_dic[category][word] / word_dic[word]


def laplace(val, total, k):
    return (val + 1) / (total + k)


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
                    category_probabilities[category] *= (1 / len(category_dic))
            else:
                category_probabilities[category] *= laplace(category_dic[category][word], word_dic[word],
                                                            len(category_dic))

        category_probabilities[category] *= category_frecuency[category]
        sum += category_probabilities[category]

    # print(category_probabilities, "\n", max(category_probabilities, key=category_probabilities.get), category_probabilities[categoria]/sum)
    return max(category_probabilities, key=category_probabilities.get)


def test_samples(dfTest, category_dic, word_dic, category_frecuency):
    hit = 0.0
    for index, row in dfTest.iterrows():
        if classify(row.titular, category_dic, word_dic, category_frecuency, row.categoria):
            hit += 1
    return hit / len(dfTest.index)


def create_confusion_array(dfTest, category_dic, word_dic, category_frecuency):
    array = [[0 for y in range(len(dfTest['categoria'].unique()))] for x in range(len(dfTest['categoria'].unique()))]
    category_hash = {}
    i = 0
    for category in dfTest['categoria'].unique():
        category_hash[category] = i
        i += 1

    for index, row in dfTest.iterrows():
        expected_value = row.categoria
        recived_value = classify(row.titular, category_dic, word_dic, category_frecuency, row.categoria)
        array[category_hash[expected_value]][category_hash[recived_value]] += 1

    return array


def confusion_matrix(dfTest, category_dic, word_dic, category_frecuency):
    array = create_confusion_array(dfTest, category_dic, word_dic, category_frecuency)
    df_cm = pd.DataFrame(array, index=[i for i in dfTest['categoria'].unique()],
                         columns=[i for i in dfTest['categoria'].unique()])
    ax = plt.figure(figsize=(10, 7))
    sn.heatmap(df_cm, annot=True, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("Ground Truth")
    plt.show()
    return array


def accuracy(array, categories):
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    category_hash = {}
    i = 0
    for category in dfTest['categoria'].unique():
        category_hash[category] = i
        i += 1

    category_accuracy = {}
    category_precision = {}
    category_f1 = {}
    category_recall = {}
    category_tp_rate = {}
    category_fp_rate = {}
    category_tp = {}
    category_fp = {}
    category_tn = {}
    category_fn = {}
    for category in categories:
        for i in range(len(array)):
            for j in range(len(array[i])):
                if i == j:
                    if category_hash[category] == i:
                        TP += array[i][j]
                    else:
                        TN += array[i][j]
                else:
                    if category_hash[category] == i:
                        FN += array[i][j]
                    if category_hash[category] == j:
                        FP += array[i][j]
                    else:
                        TN += array[i][j]

        category_tp[category] = TP
        category_fp[category] = FP
        category_tn[category] = TN
        category_fn[category] = FN
        category_accuracy[category] = (TP + TN) / (TP + TN + FP + FN)
        category_precision[category] = TP / (TP + FP)
        category_recall[category] = TP / (TP + FN)
        category_f1[category] = (2 * category_recall[category] * category_precision[category]) /\
                                (category_precision[category] + category_recall[category])
        #tasa de verdaderos positivos
        category_tp_rate[category] = TP / (TP + FN)
        #tasa de falsos positivos
        category_fp_rate[category] = FP / (FP + TN)
        print(category, ":")
        print("acuracy: ", category_accuracy[category])
        print("precision: ", category_precision[category])
        print("recall: ", category_recall[category])
        print("tp rate: ", category_tp_rate[category])
        print("fp rate: ", category_fp_rate[category])
        print("\n")
    plt.figure(figsize=(15, 7))
    plt.scatter(category_tp_rate[category],category_fp_rate[category], color='#0F9D58', s=100)
    plt.title('ROC Curve', fontsize=20)
    plt.xlabel('False Positive Rate', fontsize=16)
    plt.ylabel('True Positive Rate', fontsize=16)
    plt.show()
    return category_accuracy, category_precision, category_recall, category_f1, category_tp_rate, category_fp_rate,\
           category_tp, category_fp, category_tn, category_fn


dfTest, dfTrain = read_news(0.10)
df = pd.read_csv("test.csv")
dfTest = pd.read_csv("testSample.csv")
dfTrain = pd.read_csv("trainSample.csv")
dictionaries = make_structures(dfTrain)
calculate_frequencies(dictionaries[0], dictionaries[1])
#hitPercentage = test_samples(dfTest, dictionaries[0], dictionaries[1], category_probability(df))
array = confusion_matrix(dfTest, dictionaries[0], dictionaries[1], category_probability(df))
accuracy(array, dfTest['categoria'].unique())

#print("hit percentage", hitPercentage)
# classify("Ponsha juega al fútbol y ataja pelotas", dictionaries[0], dictionaries[1], category_probability(df))

accuracy(array, dfTest['categoria'].unique())


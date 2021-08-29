import pandas as pd


# For probability arrays, array[0] is scottish and array[1] is english #
def calculate_statistics():
    df = pd.read_excel("resources/ejercicio1.xlsx")
    grouped_by_df = df.groupby("Nacionalidad").sum()
    english_qty = (df[df["Nacionalidad"] == "I"].count())[0]
    scottish_qty = (df[df["Nacionalidad"] == "E"].count())[0]
    prob_english = english_qty / (english_qty + scottish_qty)
    prob_scottish = scottish_qty / (english_qty + scottish_qty)

    print("### Calculating statistics ###")
    print("Scottish = ", scottish_qty, ", English = ", english_qty, "\n")

    grouped_by_df.loc['E'] = grouped_by_df.loc['E'].div(scottish_qty)
    grouped_by_df.loc['I'] = grouped_by_df.loc['I'].div(english_qty)

    print("### Final statistics ###")
    print(grouped_by_df)
    return grouped_by_df, english_qty, scottish_qty, prob_english, prob_scottish


def classify(data, grouped_by_df, english_qty, scottish_qty, prob_english, prob_scottish):
    print("Testing array: ", data)
    is_scottish = 1
    is_english = 1

    for i in range(len(data)):
        if data[i] == 1:
            is_scottish *= laplace(grouped_by_df.loc['E'].iloc[i], scottish_qty)
            is_english *= laplace(grouped_by_df.loc['I'].iloc[i], english_qty)
        else:
            is_scottish *= laplace(1-grouped_by_df.loc['E'].iloc[i], english_qty)
            is_english *= laplace(1-grouped_by_df.loc['I'].iloc[i], english_qty)

    print("Is english = ", is_english * prob_english, ", Is scottish = ", is_scottish * prob_scottish)
    total = is_english * prob_english + is_scottish * prob_scottish;

    if is_english*prob_english > is_scottish*prob_scottish:
        print("IS ENGLISH!")
        print("Es ingles con = ", (is_english*prob_english)/total)
    else:
        print("IS SCOTTISH!")
        print("Es escoces con = ", (is_scottish*prob_scottish) / total)


def laplace(val, total):
    return (val+1)/(total+2)


# Main function #
test_data = [[1, 0, 1, 1, 0], [0, 1, 1, 0, 1]]
stats = calculate_statistics()

print("\n### Starting main function ###")

for row in test_data:
    classify(row, stats[0], stats[1], stats[2], stats[3], stats[4])
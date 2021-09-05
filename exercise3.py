import pandas as pd


def get_gre(gre_val, rank_val):
    val = 0
    tot = 0

    for i in range(len(df['admit'])):
        if df['rank'][i] == rank_val:
            val += 1 if df['GRE_CLASS'][i] == gre_val else 0
            tot += 1

    return laplace(val, tot, 2)


def get_gpa(gpa_val, rank_val):
    val = 0
    tot = 0

    for i in range(len(df['admit'])):
        if df['rank'][i] == rank_val:
            val += 1 if df['GPA_CLASS'][i] == gpa_val else 0
            tot += 1

    return laplace(val, tot, 2)


def add_gpa_gre_columns(gpa_val, gre_val):
    df['GPA_CLASS'] = (df['gpa'] >= gpa_val)
    df['GRE_CLASS'] = (df['gre'] >= gre_val)


def laplace(val, tot, k):
    return (val + 1) / (tot + k)


def get_admit(gpa_val, gre_val, admit_val, rank_val):
    val = 0
    tot = 0

    for i in range(len(df['admit'])):
        if df['rank'][i] == rank_val and df['GPA_CLASS'][i] == gpa_val and df['GRE_CLASS'][i] == gre_val:
            val += 1 if df['admit'][i] == admit_val else 0
            tot += 1

    return laplace(val, tot, 2)


# La productoria que vimos en la clase
def classify(gre_val, gpa_val, admit, rank):
    return get_gpa(gpa_val, rank) * get_gre(gre_val, rank) * get_admit(gre_val, gpa_val, admit, rank) * laplace((df[df["rank"] == rank].count())[0], 400, 4)


# Ejercicio 1, las clases son GPA <= 3.0 y GRE <= 500
df = pd.read_csv("resources/ejercicio3.csv")
add_gpa_gre_columns(3.0, 500)
aux = 0
for gpa in [True, False]:
    for gre in [True, False]:
        aux += classify(gre, gpa, 0, 1)

print("\n", "Ejercicio 1: P(Admitido | Rank=1)")
print(aux / laplace((df[df["rank"] == 1].count())[0], 400, 4))

# Ejercicio 2, las clases son GPA <= 3.0 y GRE <= 500
print("\n", "Ejercicio 2: P(Admitido | Rank=2, GRE=450, GPA=3.5)")
aux = get_admit(True, False, 1, 2)
total = get_admit(True, False, 1, 2) + get_admit(True, False, 0, 2)
print(aux/total)

# Ejercicio 2 bis, las clases son GPA <= 3.5 y GRE <= 450
print("\n", "Ejercicio 2 bis: P(Admitido | Rank=2, GRE=450, GPA=3.5) con categorias actualizadas a GRE<=450 y GPA<=3.5")
# Una unidad más porque queremos los menores o iguales a esos valores
add_gpa_gre_columns(3.51, 451)
aux = get_admit(False, False, 1, 2)
total = get_admit(False, False, 1, 2) + get_admit(False, False, 0, 2)
print(aux/total)


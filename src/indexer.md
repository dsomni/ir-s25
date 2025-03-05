# Building stage

- Calculate TF-IDF for all documents, filter them according to threshold and get the most significant words:
```
1) TF-IDF(docs) -> {word: score}
```
- For each document get its k-grams to build connections between k-grams and pathes of files where this k-gram is located:
```
2) for doc in docs -> {kg: [paths]}
```
- Split each word from 1) on k-grams and calculate its total score for each k-gram:
```
3) for {word: score} from 1) -> [{kg1: score}, {kg2: score}], [{kg3: score}, {kg5: score}] -> grooup by kg and sum -> {kg: total_score}
```
- Merge 2) and 3)
```
4) unite 2) and 3) -> {kg: ([paths], total_score)}
```

# Query stage

- Get prepared query words
- Split them on k-grams
- 
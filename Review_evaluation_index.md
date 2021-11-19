# 1. 基本评价指标
## 1.1. Confusion Matrix
TP — True Positive 预测为正，且实际为正
FN — False Negative 预测为负，但是预测错了（实际为正）
TN — True Negative 预测为负，且实际为负
FP — False Positive 预测为正，但是预测错了 （实际为负）
## 1.2. 假正率
False Positive Rate (FPR) = FP / (FP+TN)
## 1.3. 真正率
True Positive Rate (TPR) = TP / (FP+TN)

## 1.4. 准确率 — Accuracy
Accuracy = (TP+TN) / (TP+FP+TN+FN)
预测正确的样本数量和所有样本数量之比

## 1.5. 精确率- Precision
Precision = TP / (TP+FP)    
真正属于类别 P的/找到属于类别P的

## 1.6. 召回率（查全率）-Recall
Recall = TP / (TP+FN)
真正属于类别P的/所有属于类别P的

精确率和召回率是相互影响的，理想情况下两者都高，但是一般情况下准确率高，召回率就低；召回率高，准确率就低；
## 1.7. F1_score
F1= 2 *Precision*Recall/(Precision+Recall)
F1-score综合考虑了精确率和召回率，F1-score越高，效果越好。

## 1.8. ROC（Receiver Operating Characteristic）接受者操作特征曲线
ROC 曲线中的主要两个指标就是真正率和假正率， 中横坐标为假正率（FPR），纵坐标为真正率（TPR）

## 1.9. AUC（曲线下的面积）
为了计算 ROC 曲线上的点，我们可以使用不同的分类阈值多次评估逻辑回归模型，但这样做效率非常低。有一种基于排序的高效算法可以为我们提供此类信息，这种算法称为曲线下面积（Area Under Curve）。

AUC 的一般判断标准
0.5–0.7： 效果较低，但用于预测股票已经很不错了
0.7–0.85： 效果一般
0.85–0.95： 效果很好
0.95–1： 效果非常好，但一般不太可能

## 1.10. perplexity（困惑度）
Language Model 语言模型的评价指标<br/>
句子概率的倒数<br/>
困惑度越小句子越通顺<br/>
**句子概率**
**n-gram 模型中** 假设句子有m个单词<br/>
$ P(S)=P(w_1 w_2 ...w_m)=p(w_1)p(w_2|w_1)...P(W_m|w1,w2,...,w_m-1) $<br/>
$ PPL(W) = P(w_1 w2...w_n)^{-\frac{1}{n}}=\sqrt[n]{\frac{1}{P(w_1 w2...w_n)}} $<br/>
**神经网络**
cross entropy
$ l = -\frac{1}{N} \sum_n \sum_k t_{nk} logy_{nk} $ <br/>
$ PPL = e^l $ <br/>


# 2. 文本纠错
TP ：查错正确，原句中存在字符错误（报错正确，实际有错）<br/>
FN：-查错正确，原句中不存在字符错误（未报错，实际无错）<br/>
TN：-查错失败，原句中不存在字符错误（误报错，实际无错）<br/>
FP：-查错失败，原句中存在字符错误（未报错，实际有错，）<br/>
$ Precision = TP / (TP+FP) $ <br/>
$ Recall = TP / (TP+FN) $ <br/>
$ Accuracy = (TP+TN) / (TP+FP+TN+FN) $ <br/>
$ f1_{score} = 2 * precision * recall / (precision + recall) $ <br/>

# 3. 三元组模型
TP --> correct_num:预测正确三元组的数量 <br/>
FP --> incorrect_num: 预测错误三元组的数量 <br/>
*TN --> :没有三元组的数据，也没预测出来*(实际数据集都有三元组所以不存在) <br/>
FN --> ：有三元组的数据，没预测出来 <br/>

TP+FP --> predict_num：模型预测出来的三元组数量 <br/>
TP+FN --> gold_num: 所有真实三元组的数量 <br/>
TP+FP+FN --> all_num: 所有三元组的数量 <br/>

precision = correct_num / predict_num <br/>
Accuracy = correct_num / all_num <br/>
recall = correct_num / gold_num <br/>
f1_score = 2 * precision * recall / (precision + recall) <br/>




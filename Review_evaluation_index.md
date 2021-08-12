# 基本评价指标
## Confusion Matrix 
TP — True Positive
FN — False Negative
TN — True Negative
FP — False Positive
## 假正率
False Positive Rate (FPR) = FP / (FP+TN)
## 真正率
True Positive Rate (TPR) = TP / (FP+TN)

## 准确率 — Accuracy 
Accuracy = (TP+TN) / (TP+FP+TN+FN)
预测正确的样本数量和所有样本数量之比
## 精确率- Precision
Precision = TP / (TP+FP)    
真正属于类别P的/找到属于类别P的
## 召回率（查全率）-Recall
Recall = TP / (TP+FN)
真正属于类别P的/所有属于类别P的
精确率和召回率是相互影响的，理想情况下两者都高，但是一般情况下准确率高，召回率就低；召回率高，准确率就低；
## F1_score 
F1= 2 *Precision*Recall/(Precision+Recall)
F1-score综合考虑了精确率和召回率，F1-score越高，效果越好。

## ROC（Receiver Operating Characteristic）接受者操作特征曲线
ROC 曲线中的主要两个指标就是真正率和假正率， 中横坐标为假正率（FPR），纵坐标为真正率（TPR）

## AUC（曲线下的面积）
为了计算 ROC 曲线上的点，我们可以使用不同的分类阈值多次评估逻辑回归模型，但这样做效率非常低。有一种基于排序的高效算法可以为我们提供此类信息，这种算法称为曲线下面积（Area Under Curve）。

AUC 的一般判断标准
0.5–0.7： 效果较低，但用于预测股票已经很不错了
0.7–0.85： 效果一般
0.85–0.95： 效果很好
0.95–1： 效果非常好，但一般不太可能

## perplexity（困惑度）
句子概率的倒数 
困惑度越小句子越通顺

# 文本纠错
TP ：原句中存在字符错误，且查错正确。（有错，报错正确）
FN：-原句中不存在字符错误，且查错正确（无错，未报错）。
TN ：-原句中存在字符没有错误，但查错失败（无错，误报错）。
FP：-原句中存在字符错误，但查错失败（有错，未报错）。
Precision = TP / (TP+FP) 
Recall = TP / (TP+FN)
f1_score = 2 * precision * recall / (precision + recall)

# 三元组模型
TP --> correct_num:预测正确正确三元组的数量
TP+FP --> predict_num：模型预测出来的三元组数量
TP+FN --> gold_num: 所有真实三元组的数量

precision = correct_num / predict_num
recall = correct_num / gold_num

f1_score = 2 * precision * recall / (precision + recall)




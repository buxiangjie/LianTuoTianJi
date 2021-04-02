import pandas as pd

from typing import Optional

from decimal import Decimal, ROUND_HALF_UP


def repayment_plan(c: str, r: str, m: int, tr: Optional[str]= None):
	"""

	:param c: 本金
	:param r: 年利率
	:param m: 借款期限
	:param tr: 商户贴息率
	:return:
	"""
	c = Decimal(c).quantize(Decimal('0.00'))
	r = Decimal(r).quantize(Decimal('0.000000'))
	tr = Decimal(tr).quantize(Decimal('0.000000'))
	if r<= 0.1:
		if r + tr != Decimal('0.1'):
			raise IOError
	col = ['本金', '应还本息', '应还本金', '应还利息', '剩余本金', '贴息']
	df = pd.DataFrame(
		[[0 for i in range(len(col))] for j in range(m + 1)],
		index=list(range(m + 1)),
		columns=col
	)
	df.iloc[0, 0] = c
	if r == 0:
		month_r = 0
		df.iloc[:, 1] = (c * month_r * (1 + month_r) ** m / ((1 + month_r) ** m - 1)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	else:
		month_r = Decimal(r / 12).quantize(Decimal('0.0000000000000000000000'), rounding=ROUND_HALF_UP)
		df.iloc[:, 1] = (c * month_r * (1 + month_r) ** m / ((1 + month_r) ** m - 1)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
	one_period_all_pay = df.iloc[0,1].quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
	total_interest = one_period_all_pay * m - df.iloc[0, 0].quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
	i = 0
	for i in range(m):
		j = i + 1
		interest = df.iloc[i, 0] * month_r
		#计算应还利息
		interests = Decimal(str(interest)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
		if i != m-1:
			total_interest -= interests
			df.iloc[i, 3] = interests
		else:
			end_interest = interests - total_interest + total_interest
			df.iloc[i, 3] = Decimal(str(end_interest)).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
			df.iloc[i, 1] = df.iloc[i, 0] + df.iloc[i, 3]
		#计算应还本金
		if i != m-1:
			df.iloc[i, 2] = df.iloc[i, 1] - df.iloc[i, 3]
		else:
			df.iloc[i, 2] = df.iloc[i, 0]
		if tr:
			mtr = Decimal(str(tr/12)).quantize(Decimal('0.00000000000000000000'), rounding=ROUND_HALF_UP)
			trs = Decimal(df.iloc[i, 0]) * mtr
			df.iloc[i, 5] = Decimal(str(trs)).quantize(Decimal('0.00'),rounding=ROUND_HALF_UP)
		#计算剩余本金
		df.iloc[i, 4] = df.iloc[i, 0] - df.iloc[i, 2]
		#计算下一期本金
		df.iloc[j, 0] = df.iloc[i, 4]
		i += 1
	df = df.iloc[0:m, :]
	df.index = range(1, m + 1)
	# df.to_csv("list_stock.csv", encoding="utf-8", index=False)
	return df


if __name__ == '__main__':
	print(repayment_plan("50000", "0.03", 12, "0.070000"))
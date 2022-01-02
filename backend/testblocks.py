import psycopg2
import requests
from models import Transaction
from tqdm import tqdm
import sys
start_block =int(sys.argv[1])
end_block = int(sys.argv[2])
list = []

for i in tqdm(range(start_block, end_block)):
	if Transaction.select().where(Transaction.height==i).limit(1).count()==0:
		list.append(i)
print(list)

from pathlib import Path
from fractions import Fraction as F
import json, random, base64
from PIL import Image

ROOT=Path(__file__).parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
ASSETS=OUT/'assets'/'images'; ASSETS.mkdir(parents=True,exist_ok=True)

# Each expression is transcribed from the supplied worksheet; values use exact rational arithmetic.
chapters=[
 [('-11/10 * 14/3','紙卡1'),('-7/5 * -1/6','紙卡1'),('2/3 * -9/10','紙卡1'),('-3/8 * -4/7','紙卡1'),('-12/7 * -13/8','紙卡2'),('-8/9 * -5/2','紙卡2'),('-4/5 * 3/4','紙卡3'),('2/3 * -10/9','紙卡3'),('-3/4 * -11/2','紙卡4')],
 [('8/7 / -7/2','紙卡1'),('-5/2 / -3/2','紙卡1'),('-33/10 / 22/15','紙卡1'),('3/2 / -11/10','紙卡2'),('33/10 / -22/15','紙卡2'),('-3/8 / -7/4','紙卡2'),('-31/7 / -31/28','紙卡2'),('-4 / -17/4','紙卡3'),('5/3 / -25/4','紙卡3')],
 [('-21/5 / 35/11 * -5/9','紙卡1'),('-5/4 / 8/3 / 5/2','紙卡2'),('-4/5 * -10/9 * -3','紙卡2'),('7/5 * -1/6','紙卡3'),('-2/9 / -13/6 / -14/3','紙卡3'),('-11/3 / 9/4 / -11/6','紙卡3'),('-3/8 * -6/9 * -5/6','紙卡3'),('-7/2 / 6/7 / -49/12','紙卡4'),('49/15 / -14/45','紙卡4')]
]

def calc(expr):
 t=expr.split(); result=F(t[0]); steps=[str(result)]
 for op,value in zip(t[1::2],t[2::2]):
  v=F(value); result=result*v if op=='*' else result/v; steps.append(str(result))
 return result,steps
def display(expr):
 t=expr.split(); return ' '.join('×' if x=='*' else '÷' if x=='/' else '('+x.replace('-', '−')+')' if x.startswith('-') else x for x in t)
bank=[]; rng=random.Random(42)
for c,rows in enumerate(chapters):
 qs=[]
 for expr,source in rows:
  val,steps=calc(expr)
  exp='先判斷正負號：同號相乘或相除得正，異號得負。帶分數要先化成假分數。'
  if '/' in expr.split()[1::2]: exp+='除以一個非零分數，等於乘以它的倒數；連續乘除由左到右計算。'
  else: exp+='分子乘分子、分母乘分母，先交叉約分可減少計算。'
  exp+=' 本題：'+display(expr)+' = '+' → '.join(steps[1:])+ '（最簡分數）。'
  qs.append(dict(prompt=display(expr)+' = ？',value=str(val),explanation=exp,source=source,expr=expr))
 # Cooperative boss is an original adaptation of the source activity, not another worksheet card.
 vals=[F(-2,3),F(3,4),F(-4,5),F(5,2)] if c==0 else [F(-16,49),F(-3,16),F(-7,30),F(-11,2)] if c==1 else [F(-3,5),F(3,14),F(-4,15),F(-21,2)]
 val=F(1)
 for v in vals: val*=v
 qs.append(dict(prompt='四位同門算出的答案依序為 '+ '、'.join(str(v).replace('-','−') for v in vals)+'。四個答案的乘積是多少？',value=str(val),explanation='四人合陣要把四個答案全部相乘，先數負號，再交叉約分。'+' × '.join('('+str(v)+')' for v in vals)+' = '+str(val)+'。任一人的答案有誤，都會影響最後的乘積；可以交換驗算。',source='依教材合作活動改編',expr=' * '.join(str(v) for v in vals)))
 for q in qs:
  v=F(q['value']); candidates=[v,-v,v+1,v-1,F(v.denominator,v.numerator) if v else F(2),v*2]
  unique=[]
  for x in candidates:
   if x not in unique: unique.append(x)
  opts=unique[:4]; rng.shuffle(opts)
  q['options']=[str(x) for x in opts];q['answerIndex']=opts.index(v)
 bank.append(qs)
assert all(len(x)==10 for x in bank)
for chapter in bank:
 for q in chapter:
  assert calc(q['expr'])[0]==F(q['value'])
  assert sum(F(x)==F(q['value']) for x in q['options'])==1
(OUT/'question-bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding='utf8')

template=(ROOT/'game-template.html').read_text(encoding='utf8')
template=template.replace('__BANK__',json.dumps(bank,ensure_ascii=False))
manifest=json.loads((ROOT/'asset-paths.json').read_text(encoding='utf8'))
for name,src in manifest.items():
 im=Image.open(src)
 if name!='arena':
  im=im.convert('RGBA'); assert im.getextrema()[3][0]==0, 'Expected transparent sprite'
  im.thumbnail((800,800)); im.save(ASSETS/(name+'.png'))
  im.save(ASSETS/(name+'.webp'),quality=89)
  data=(ASSETS/(name+'.webp')).read_bytes(); mime='image/webp'
 else:
  im=im.convert('RGB'); im.thumbnail((1600,1000)); im.save(ASSETS/'arena.jpg',quality=88)
  data=(ASSETS/'arena.jpg').read_bytes(); mime='image/jpeg'
 template=template.replace('__'+name.upper()+'__','data:'+mime+';base64,'+base64.b64encode(data).decode())
(OUT/'index.html').write_text(template,encoding='utf8')
print('Built output/index.html; verified 30 exact rational answers and transparent sprites.')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

### get cheese journal data
chz = pd.read_excel('cheese_ratings.xlsx')
chz['combined_rating'] = (chz['a_rating'] + chz['j_rating']) / 2

### analyze data
chz = chz.loc[~np.isnan(chz['a_rating'])]
a = chz['a_rating'].loc[~np.isnan(chz['a_rating'])]
j = chz['j_rating'].loc[~np.isnan(chz['j_rating'])]
d = chz['date']

### histogram
cols = ['#8da0cb', '#fc8d62']
fig, ax = plt.subplots(1,1, figsize=(8,5))

ax.hist(j, color=cols[0], alpha=0.6, label=['Julie'], bins=np.arange(0, 5.1, 0.5))
ax.hist(a, color=cols[1], alpha=0.6, label=['Andrew'], bins=np.arange(0, 5.1, 0.5))
ax.legend(loc='upper left')
ax.set_xlabel('Rating')
ax.set_yticks([])
plt.savefig('figs/hist.png', dpi=300, bbox_inches='tight')

### boxplots by place of origin
fig, ax = plt.subplots(1,1, figsize=(8,5))
sns.boxplot(data=chz.sort_values('origin'), y='combined_rating', x='origin', ax=ax)
_ = ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.savefig('figs/boxplots_origin.png', dpi=300, bbox_inches='tight')

### boxplots by style
fig, ax = plt.subplots(1,1, figsize=(8,5))
sns.boxplot(data=chz.sort_values('style'), y='combined_rating', x='style', ax=ax)
_ = ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
plt.savefig('figs/boxplots_style.png', dpi=300, bbox_inches='tight')

### timeseries of ratings
fig, ax = plt.subplots(1,1, figsize=(8,5))
a.index = chz['date']
j.index = chz['date']
ax.plot(j.rolling(5).mean(), c=cols[0], label='Julie')
ax.plot(a.rolling(5).mean(), c=cols[1], label='Andrew')
ax.fill_between(j.index, j.rolling(5).min(), j.rolling(10).max(), color=cols[0], alpha=0.2)
ax.fill_between(a.index, a.rolling(5).min(), a.rolling(10).max(), color=cols[1], alpha=0.2)
ax.plot(j, marker='o', lw=0, c=cols[0], alpha=0.5)
ax.plot(a, marker='o', lw=0, c=cols[1], alpha=0.5)
ax.legend()
ax.xaxis.set_tick_params(rotation=45)
plt.savefig('figs/rolling_avg.png', dpi=300, bbox_inches='tight')

### wordcloud, adapting from https://www.geeksforgeeks.org/generating-word-cloud-python/
from wordcloud import WordCloud, STOPWORDS

comment_words = ''
stopwords = set(STOPWORDS)

# iterate through the csv file
for val in chz['a_comments']:
    # typecaste each val to string
    val = str(val)
    # split the value
    tokens = val.split()
    # Converts each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
    comment_words += " ".join(tokens)+" "

# iterate through the csv file
for val in chz['j_comments']:
    # typecaste each val to string
    val = str(val)
    # split the value
    tokens = val.split()
    # Converts each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
    comment_words += " ".join(tokens)+" "

wordcloud = WordCloud(width = 800, height = 800,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(comment_words)

# plot the WordCloud image
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad = 0)
plt.savefig('figs/wordcloud.png', dpi=300, bbox_inches='tight')



#######################################
### print data to markdown files for website
####################################
import subprocess

### sort cheeses by style
subprocess.run(["cp", "bystyle_base.rst", "bystyle.rst"])
styles = list(set(chz['style']))
styles.sort()
styles = [s for s in styles if s != 'Other' ]
styles += ['Other']

imgs = glob.glob('cheesepics/*')

### now loop over cheeses from excel file
with open('bystyle.rst', 'a') as f:
    for style in styles:
        f.write(f'\n   {style}')

for style in styles:
    with open(f'{style}.rst', 'w') as f:
        f.write(f'{style} \n')
        f.write(f'====================== \n')
        chz_style = chz.loc[chz['style'] == style, :]
        chz_style = chz_style.sort_values('name').reset_index(drop=True)
        for i in range(chz_style.shape[0]):
            c = chz_style.iloc[i, :]
            f.write(f"{c['name']} ({c['maker']})\n")
            f.write(f'----------------- \n')
            if isinstance(c['image'], str):
                img = [s for s in imgs if c["image"] in s][0]
                f.write(f'.. image:: {img} \n')
                f.write(f'        :align: right \n')
                f.write(f'        :height: 200px \n\n')

            f.write(f"- **Origin**: {c['origin']}\n")
            f.write(f"- **Milk**: {c['milk']}\n")
            f.write(f"- **Purchase location**: {c['store']}\n")
            f.write(f"- **Purchase date**: {c['date'].strftime('%m/%d/%y')}\n")
            if isinstance(c['j_comments'], str):
                f.write(f"- **Julie's comments**: {c['j_comments']}  ")
                if not np.isnan(c['j_rating']):
                    f.write(f"**{c['j_rating']}/5**\n")
                else:
                    f.write("\n")
            if isinstance(c['a_comments'], str):
                f.write(f"- **Andrew's comments**: {c['a_comments']}  ")
                if not np.isnan(c['a_rating']):
                    f.write(f"**{c['a_rating']}/5**\n")
                else:
                    f.write("\n")
            if isinstance(c['provenance'], str):
                f.write(f"- **Thanks to {c['provenance']} for this cheese!**\n")
            f.write('\n')
        f.write('\n')


### sort cheeses by origin
subprocess.run(["cp", "byorigin_base.rst", "byorigin.rst"])
origins = list(set(chz['origin']))
origins.sort()

imgs = glob.glob('cheesepics/*')

### now loop over cheeses from excel file
with open('byorigin.rst', 'a') as f:
    for origin in origins:
        f.write(f'\n   {origin}')
    
for origin in origins:
    with open(f'{origin}.rst', 'w') as f:
        f.write(f'{origin} \n')
        f.write(f'====================== \n')
        chz_origin = chz.loc[chz['origin'] == origin, :]
        chz_origin = chz_origin.sort_values('name').reset_index(drop=True)
        for i in range(chz_origin.shape[0]):
            c = chz_origin.iloc[i, :]
            f.write(f"{c['name']} ({c['maker']})\n")
            f.write(f'----------------- \n')
            if isinstance(c['image'], str):
                img = [s for s in imgs if c["image"] in s][0]
                f.write(f'.. image:: {img} \n')
                f.write(f'        :align: right \n')
                f.write(f'        :height: 200px \n\n')

            f.write(f"- **Style**: {c['style']}\n")
            f.write(f"- **Milk**: {c['milk']}\n")
            f.write(f"- **Purchase location**: {c['store']}\n")
            f.write(f"- **Purchase date**: {c['date'].strftime('%m/%d/%y')}\n")
            if isinstance(c['j_comments'], str):
                f.write(f"- **Julie's comments**: {c['j_comments']}  ")
                if not np.isnan(c['j_rating']):
                    f.write(f"**{c['j_rating']}/5**\n")
                else:
                    f.write("\n")
            if isinstance(c['a_comments'], str):
                f.write(f"- **Andrew's comments**: {c['a_comments']}  ")                
                if not np.isnan(c['a_rating']):
                    f.write(f"**{c['a_rating']}/5**\n")
                else:
                    f.write("\n")                
            if isinstance(c['provenance'], str):
                f.write(f"- **Thanks to {c['provenance']} for this cheese!**\n")
            f.write('\n')
        f.write('\n')


### sort cheeses by rating
subprocess.run(["cp", "byrating_base.rst", "byrating.rst"])
ratings = chz.sort_values('combined_rating', ascending=False)

imgs = glob.glob('cheesepics/*')

### now loop over cheeses from excel file
with open('byrating.rst', 'a') as f:
    for i in range(ratings.shape[0]):
        c = ratings.iloc[i, :]
        f.write(f"{i+1}. {c['name']} ({c['maker']})\n")
        f.write(f'----------------- \n')
        if isinstance(c['image'], str):
            img = [s for s in imgs if c["image"] in s][0]
            f.write(f'.. image:: {img} \n')
            f.write(f'        :align: right \n')
            f.write(f'        :height: 200px \n\n')

        f.write(f"- **Style**: {c['style']}\n")
        f.write(f"- **Origin**: {c['origin']}\n")
        f.write(f"- **Milk**: {c['milk']}\n")
        f.write(f"- **Purchase location**: {c['store']}\n")
        f.write(f"- **Purchase date**: {c['date'].strftime('%m/%d/%y')}\n")
        if isinstance(c['j_comments'], str):
            f.write(f"- **Julie's comments**: {c['j_comments']}  ")
            if not np.isnan(c['j_rating']):
                f.write(f"**{c['j_rating']}/5**\n")
            else:
                f.write("\n")
        if isinstance(c['a_comments'], str):
            f.write(f"- **Andrew's comments**: {c['a_comments']}  ")                
            if not np.isnan(c['a_rating']):
                f.write(f"**{c['a_rating']}/5**\n")
            else:
                f.write("\n")                
        if isinstance(c['provenance'], str):
            f.write(f"- **Thanks to {c['provenance']} for this cheese!**\n")
        f.write('\n')







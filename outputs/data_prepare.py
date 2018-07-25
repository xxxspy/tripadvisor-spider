import pandas as pd 
from pathlib import Path




def user_ratings(reviews):
    ratings = {}
    for user_name, subdf in reviews.groupby('user_name'):
        point = subdf['point'].tolist()
        ratings[user_name] = point
    return ratings

def neighber_rattings(neighbors):
    rtn = {}
    for (attr_url,cat), subdf in neighbors.groupby(['attraction_href', 'category']):
        names, ratings = list(subdf['name']), list(subdf['rating'])
        rtn[(attr_url, cat)] = dict(zip(names, ratings))
        print(rtn[(attr_url, cat)])
    return rtn


def organize(reviews, neightbors):
    cols = ['attraction', 'attraction_href',
            'content', 'likes', 'point', 'shares', 'title', 'user_name']
    print('Geting user rattings')
    urate = user_ratings(reviews)
    all_rate = lambda user_name: urate[user_name]
    count_rate = lambda user_name: len(all_rate(user_name))
    print('Getting nei_rattings')
    nei_ratings = neighber_rattings(neighbors)
    # get_nei = lambda attr_url, cat: nei_ratings[(attr_url, cat)]
    print('Getting neighbors')
    # reviews['neightbors'] = reviews['attraction_href'].map(get_nei)
    print('geting all usre rattings')
    reviews['all_user_rate'] = reviews['user_name'].map(all_rate)
    print('Counting user rattings')
    reviews['count_user_rate'] = reviews['all_user_rate'].map(len)
    cats = ('附近的餐厅', '附近的酒店', '附近的景点')
    for c in cats:
        print(f'getting {c}')
        reviews[c] = reviews['attraction_href'].map(lambda x:nei_ratings.get((x, c)))
    return reviews




if __name__ == '__main__':
    here = Path(__file__).parent.absolute()
    reviews = pd.read_csv(here / 'review.csv')
    neighbors = pd.read_csv(here / 'neighbor.csv')
    reviews = organize(reviews, neighbors)
    output = here / 'organized_data.csv'
    print('Wrting......')
    reviews.to_csv(output)

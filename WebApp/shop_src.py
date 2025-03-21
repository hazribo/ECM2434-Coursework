from .models import ShopItem

SHOP_ITEMS = [
    {
        "name" : "item1",
        "cost" : 2,
        "thPath" : "item1.png"
    },
    {
        "name" : "item2",
        "cost" : 3,
        "thPath" : "item2.png"
    }
   
]



class ShopItemData:
    name = None
    cost = None
    thpath = None
    buyurl = None


def generate_bean_with_cosmetics(userid):
    pass;



def user_buy(profile, itemname):
    pass;

    item = ShopItem.objects.get(name=itemname)

    cost = item.cost;
    uCredits = profile.credits;

    if cost > uCredits:
        return False

    profile.inventory.add(item)
    profile.credits -= cost;
    profile.save()

    print(item.name)

    return True


def distillItemData(item):
    data = ShopItemData()
    data.name = item.name
    data.cost = item.cost
    data.thpath = item.name + ".png"
    data.buyurl = f"shop/{item.name}/"
    return data

def get_inventory_items(profile):
    items = [distillItemData(item) for item in profile.inventory.all()]
    return items

def get_shop_items():
    items = [distillItemData(item) for item in ShopItem.objects.all()]
    return items





def shop_init():

    if len(ShopItem.objects.all()) == len(SHOP_ITEMS):
        print("added all")
        return
    
    ShopItem.objects.all().delete()

    for index, item in enumerate(SHOP_ITEMS):
        shItem = ShopItem.objects.create(
            name=item["name"], cost=item["cost"],
            # thpath = item["thPath"]
        )
        shItem.save()
        
        
shop_init()
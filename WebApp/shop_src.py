from .models import ShopItem

SHOP_ITEMS = [

    {"name" : "AllBlackShoes",  "cost" : 1, "thPath" : "cosmetics/AllBlackShoes.png" },
    {"name" : "BlackShoes",     "cost" : 1, "thPath" : "cosmetics/BlackShoes.png" },
    {"name" : "BlueShoes",      "cost" : 1, "thPath" : "cosmetics/BlueShoes.png" }, 
    {"name" : "BrownShoes",     "cost" : 1, "thPath" : "cosmetics/BrownShoes.png" },
    {"name" : "GreenShoes",     "cost" : 1, "thPath" : "cosmetics/GreenShoes.png" },
    {"name" : "PinkShoes",      "cost" : 1, "thPath" : "cosmetics/PinkShoes.png" },
    {"name" : "RedShoes",       "cost" : 1, "thPath" : "cosmetics/RedShoes.png" },

    {"name" : "RedCap",         "cost" : 3, "thPath" : "cosmetics/RedCap.png" },
    {"name" : "BlackCap",       "cost" : 3, "thPath" : "cosmetics/BlackCap.png" },

    {"name" : "BlueTopHat",     "cost" : 2, "thPath" : "cosmetics/BlueTopHat.png" },
    {"name" : "BrownHat",       "cost" : 2, "thPath" : "cosmetics/BrownHat.png" },
    {"name" : "PirateHat",      "cost" : 2, "thPath" : "cosmetics/PirateHat.png" },
    {"name" : "RedTopHat",      "cost" : 2, "thPath" : "cosmetics/RedTopHat.png" },
    {"name" : "CowboyHat",      "cost" : 2, "thPath" : "cosmetics/CowboyHat.png" },
   
]



class ShopItemData:
    name = None
    cost = None
    thpath = None
    buyurl = None





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
    data.thpath = r"cosmetics/" + item.name + ".png"
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
    
    if ShopItem.objects.count() > len(SHOP_ITEMS):
        ShopItem.objects.all().delete()

    for index, item in enumerate(SHOP_ITEMS):
        shItem = ShopItem.objects.create(
            name=item["name"], cost=item["cost"],
            # thpath = item["thPath"]
        )
        shItem.save()
        
        
# shop_init()
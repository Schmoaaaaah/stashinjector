from stashapi.stashapp import StashInterface
import sqlite3


def test():
    con = sqlite3.connect("user_data.db")
    cur = con.cursor()
    res = cur.execute(
        "select posts.post_id, posts.text, medias.filename, medias.media_id, medias.directory, medias.link, medias.created_at from posts inner join medias on posts.post_id = medias.post_id")
    medias = res.fetchall()

    stash = StashInterface({
        "scheme": "http",
        "domain": "192.168.188.21",
        "port": "9997"
    })
    performername = medias[0][4].split("/")[3]
    performerid = stash.find_performers({"name": {"modifier": "INCLUDES", "value": performername}})
    if len(performerid) == 0:
        performerid = []
        performerid[0] = stash.create_performer({"name": performername})
    StudioName = medias[0][4].split("/")[2]
    StudioID = stash.find_studios({"name": {"modifier": "INCLUDES", "value": StudioName}})
    if len(StudioID) == 0:
        StudioID = []
        StudioID[0] = stash.create_studio({"name": StudioName})
    for media in medias:
        if ".mp4" in media[2]:
            ssearch = media[2].split("_")[0]
            scene_data = stash.find_scenes({"path": {"modifier": "INCLUDES", "value": ssearch}})
            if len(scene_data) == 1:
                sscene = {
                    "id": scene_data[0]["id"],
                    "title": media[1].split("\n")[0],
                    "details": media[1],
                    "url": media[5],
                    "date": media[6].split(".")[0].split(" ")[0],
                    "performer_ids": [performerid[0]["id"]],
                    "studio_id": StudioID[0]["id"],
                }
                uscene = stash.update_scene(sscene)
                print("Scene Updated: ")
                print(uscene)
        elif ".jpg" in media[2]:
            isearch = media[2].split("_")[1].split(".")[0]
            iquery = """
            query FindImages($isearch:String!)  {
	            findImages(image_filter:{path: { modifier:INCLUDES, value: $isearch } } ){
		            images {
			            id
		            }
                }
            }
            """
            image_data = stash.call_gql(iquery, {"isearch": isearch})
            if len(image_data) == 1:
                simage = {
                    "id": image_data['findImages']['images'][0]["id"],
                    "title": media[1].split("\n")[0],
                    "url": media[5],
                    "date": media[6].split(".")[0].split(" ")[0],
                    "performer_ids": [performerid[0]["id"]],
                    "studio_id": StudioID[0]["id"],
                }
                uimage = stash.update_image(simage)
                print("Image Updated: ")
                print(uimage)


if __name__ == '__main__':
    test()

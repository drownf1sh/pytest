import requests


api_list = [
    "http://0.0.0.0:5000/api/rec/mktplace/event_for_you?user_id=159429228213465",
    "http://0.0.0.0:5000/api/rec/mktplace/recommended_for_you?user_id=18691769974905",
    "http://0.0.0.0:5000/api/rec/mktplace/popular_item",
]

memory_debug_file = open("memory_test_result.txt", "a")

for api in api_list:
    # warm up
    for i in range(2):
        requests.get(api)

    # get memory usage before calling api
    minfo = requests.get("http://0.0.0.0:5000/api/rec/healthcheck/memory")
    memory_before = minfo.json().get("memory")
    memory_debug_file.write(f"Before Calling API: {str(memory_before)} \n")
    print(f"Before Calling API: {str(memory_before)}")

    # get memory usage snapshot
    minfo = requests.get("http://0.0.0.0:5000/api/rec/healthcheck/snapshot")
    print(minfo.json().split("\n"))

    for i in range(20):
        requests.get(api)

    # get memory usage after calling api
    minfo = requests.get("http://0.0.0.0:5000/api/rec/healthcheck/memory")
    memory_after = minfo.json().get("memory")
    memory_debug_file.write(f"After Calling API: {str(memory_before)} \n")
    print(f"After Calling API: {str(memory_after)}")

    memory_diff = memory_after - memory_before
    memory_debug_file.write(f"Memory Increased by: {memory_diff} MB \n")
    print(f"Memory Increased by: {memory_diff} MB")

    # get another memory usage snapshot
    minfo = requests.get("http://0.0.0.0:5000/api/rec/healthcheck/snapshot")
    memory_debug_file.write(f"Memory Usage for API {api} \n")
    print(f"Memory Usage for API {api}")
    for stat in minfo.json().split("\n"):
        memory_debug_file.write(f"{stat} \n")
        print(stat)

memory_debug_file.close()

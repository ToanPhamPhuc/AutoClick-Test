# import pyautogui
# import time

# def click_button(image_path, description, timeout=10):
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
#         if location:
#             pyautogui.click(location)
#             #print(f"Clicked {description} at {location}")
#             return True
#         time.sleep(0.5)
#     #print(f"{description} not found within timeout.")
#     return False

# #print("Starting... You have 5 seconds to switch to the app window.")
# time.sleep(5)

# while True:
#     # Step 1: Skip button
#     click_button("bo_qua.png", "Bỏ qua")
#     time.sleep(1)

#     # Step 2: Next step ("Tiếp tục") - try both variants
#     if not click_button("tiep_tuc.png", "Tiếp tục (question screen)"):
#         click_button("tiep_tuc.png", "Tiếp tục (end screen)")

#     time.sleep(3)

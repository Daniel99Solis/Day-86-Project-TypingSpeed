# --------------------------- Typing Speed App ------------------------------------- #
from tkinter import *
from tkinter.ttk import *  # Add styling to elements by creating style objects
import requests

from customs_widgets import TextScrollCombo

# Variables
text_list = []  # List with the words the user needs to type without spaces
word_number = 0  # Integer to keep track of the current word
position_word = 0  # Integer to keep track of the position letter of the word
position_text = 0  # Integer to keep track of the text inside the TextArea field
right_words = 0  # Integer to keep track the good words typed
bad_words = 0  # Integer to keep track the bad words typed
list_mistakes = []  # List to keep track of the bad typing the user might have
list_correct_words = []  # List to save the correct spelling of the list_mistakes
time = 60  # Variable to set the seconds to the timer
timer_on = False  # Boolean to check if the user still has time
timer = ""  # Variable to call a window.after method to keep track of time in the window

cpm = 0  # Counting the number of total characters type
wpm = 0  # Counting the number of total words type


def get_text():
    """Function to get the text the user will need to type"""
    global text_list
    response = requests.get("https://random-word-api.vercel.app/api?words=60")
    response.raise_for_status()
    text_list = response.json()
    text.config(state="normal", foreground="black")
    text.delete("1.0", "end")
    for word in text_list:
        text.insert(END, word)
        text.insert(END, " ")
    text.tag_add("first", f"1.0", f"1.{len(text_list[0])}")
    text.tag_config("first", background="#6499E9")
    text.config(state="disabled")
    print(text_list)


def on_entry_click(event):
    """Function to delete the placeholder inside the Entry when the user is typing something"""
    if user_input.get() == "Type the words here":
        user_input.delete(0, END)
        user_input.configure(foreground="black")


def on_focus_out(event):
    """Function to put a placeholder inside the Entry when the user is not typing something"""
    if user_input.get() == "":
        user_input.insert(0, "Type the words here")
        user_input.configure(foreground="gray")


def compare(event):
    """This function will be the brain of the program controlling the logic of the TextArea field and what the user
       types in the Entry"""
    global timer_on, position_text, word_number, position_word, right_words, bad_words, time
    global cpm, list_correct_words, list_mistakes
    text.config(state="normal")  # Active TextArea to put text on it

    # Activate timer if it is not activate
    if not timer_on:
        timer_on = True
        timer_run(time)

    letters_word = list(text_list[word_number])
    print(letters_word)

    # Check if the user type "BackSpace" to delete a character he or she had typed
    if event.keysym == "BackSpace":
        print(user_input.get())
        if 0 < position_word <= len(letters_word) and len(user_input.get()) <= len(letters_word):
            print("You are deleting")
            current_letter = position_text
            position_text -= 1
            position_word -= 1
            text.delete(f"1.{position_text}", f"1.{current_letter}")
            text.insert(f"1.{position_text}", letters_word[position_word])
            text.tag_add(f"delete{position_text}", f"1.{position_text}", f"1.{current_letter}")
            text.tag_config(f"delete{position_text}", foreground="black", background="#6499E9")
    # Check if the user has type space
    elif event.keysym == "space":
        # If statement to see if the user type the correct word
        if user_input.get().lstrip() == text_list[word_number]:
            right_words += 1
        else:
            bad_words += 1
            list_mistakes.append(user_input.get().lstrip())
            list_correct_words.append(text_list[word_number])
        print("------ Current Score --------- ")
        print(f"Right Words: {right_words}")
        print(f"Bad Words: {bad_words}")

        # Delete what there is inside the Entry
        user_input.delete(0, END)

        # Check if the user hasn't typed all the letter in the current word and if so, add them incorrectly
        if position_word != len(letters_word):
            pos_to_delete = (len(letters_word) - position_word + position_text)
            text.delete(f"1.{position_text}", f"1.{pos_to_delete + 1}")
            remain_text = ''.join(letters_word[position_word:]) + " "
            text.insert(f"1.{position_text}", remain_text)
            text.tag_add(f"remain{word_number}", f"1.{position_text}", f"1.{pos_to_delete}")
            text.tag_config(f"remain{word_number}", foreground="red")
            position_text += len(remain_text)
        else:
            position_text += 1
        position_word = 0
        word_number += 1

        # Highlighting the next word to be type
        next_word = text_list[word_number]
        text.tag_add(f"highlight", f"1.{position_text}", f"1.{position_text + len(next_word)}")
        text.tag_config(f"highlight", background="#6499E9")

    # If the type was actually a letter check if the user's type corresponds to the current letter and send feedback
    # by colors
    elif event.keysym == letters_word[position_word]:
        text.delete(f"1.{position_text}")
        text.insert(f"1.{position_text}", event.keysym)
        text.tag_add(f"pos{position_text}", f"1.{position_text}")
        text.tag_config(f"pos{position_text}", foreground="green")
        position_text += 1
        position_word += 1
        cpm += 1
    else:
        text.delete(f"1.{position_text}")
        text.insert(f"1.{position_text}", letters_word[position_word])
        text.tag_add(f"pos{position_text}", f"1.{position_text}")
        text.tag_config(f"pos{position_text}", foreground="red")
        position_text += 1
        position_word += 1

    text.config(state="disabled")  # Disabled TextArea to block user to type in it


def timer_run(seconds):
    """Function to call the window.after methods to show the time to the user"""
    global timer
    canvas.itemconfig(timer_text, text=f"Time Left: {seconds}s")
    if seconds > 0:
        timer = window.after(1000, timer_run, seconds - 1)
    else:
        user_input.config(state="disabled")
        window.after_cancel(timer)
        label_app.grid_forget()
        restart_b.grid_forget()
        canvas.grid_forget()
        text.grid_forget()
        user_input.grid_forget()

        show_results()  # After the time expires we call this function


def restart():
    """Function to restart the app"""
    global word_number, position_word, position_text, right_words, bad_words, time
    global timer_on, timer, cpm, text_list, list_mistakes, list_correct_words

    print(time)
    # Rearrange the app in case the results have been shown
    if time <= 0:
        label_app.pack_forget()
        restart_b.pack_forget()
        canvas_result.pack_forget()

        label_app.grid(row=0, column=0, columnspan=3, padx=10, pady=10)
        canvas.grid(row=1, column=1)
        restart_b.grid(row=1, column=2)
        text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        user_input.config(state="normal")  # Reactive the user to be able to type again
        user_input.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    # Reset variables
    word_number = 0  # Integer to keep track of the current word
    position_word = 0  # Integer to keep track of the position letter of the word
    position_text = 0  # Integer to keep track of the text inside the TextArea field
    right_words = 0  # Integer to keep track the good words typed
    bad_words = 0  # Integer to keep track the bad words typed
    list_mistakes = []  # List to keep track of the bad typing the user might have
    list_correct_words = []  # List to save the correct spelling of the list_mistakes
    time = 60  # Variable to set the seconds to the timer
    timer_on = False  # Boolean to check if the user still has time
    cpm = 0  # Counting the number of total characters type

    # Restart the text to type with the next function
    get_text()

    # Restart the TextSrollCombo
    mistakes.txt.config(state="normal")
    mistakes.txt.delete("1.0", "end")

    # Restart the timer
    canvas.itemconfig(timer_text, text="Time Left: 60s")
    window.after_cancel(timer)

    # Restart the user input
    user_input.delete(0, END)


def show_results():
    """Function to show the results of the test"""
    global cpm, wpm, time, bad_words, list_correct_words, list_mistakes
    label_app.pack(pady=10)
    restart_b.pack()
    wpm = round(cpm / 5)
    canvas_result.itemconfig(cpm_score, text="Your Score is: ")
    canvas_result.itemconfig(cpm_result, text=f"{cpm} CPM ")
    canvas_result.itemconfig(wpm_score, text="is equal to: ")
    canvas_result.itemconfig(wpm_result, text=f"{wpm} WPM")
    if bad_words == 0:
        canvas_result.itemconfig(wrong_words, text="Congratulations you had no mistakes", fill="#6499E9")
        canvas_result.itemconfig(encourage_message, text="")
        canvas_result.itemconfig(mistakes_window, state="hidden")
        canvas_result.itemconfig(congrats_im, state="normal")
    else:
        canvas_result.itemconfig(congrats_im, state="hidden")
        canvas_result.itemconfig(wrong_words, text=f"You had {bad_words} wrong words,", fill="#ff9966")
        canvas_result.itemconfig(encourage_message, text="but don't worry is just practice")
        canvas_result.itemconfig(mistakes_window, state="normal")
        mistakes.txt.config(state="normal")
        for i in range(0, bad_words):
            mistakes.txt.insert("1.0", f"• instead of '{list_correct_words[i]}', you typed '{list_mistakes[i]}'.\n")
        mistakes.txt.config(state="disabled")
    canvas_result.pack(pady=20, padx=20)

    time = 0  # The time is equal to 0 now


# Window
window = Tk()
window.title("Typing Speed App")
window.minsize(width=500, height=400)
window.maxsize(width=1000, height=800)
window.config(bg="#6499E9", padx=15, pady=15)

# Name App Label
label_app = Label(text="Typing Speed App", font=("Times", 24, "italic"),
                  background="#6499E9", foreground="#9EDDFF", justify="center")
label_app.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

# Canvas to show the timer inside a text element
canvas = Canvas(width=140, height=20, bg="#6499E9", highlightthickness=0)
timer_text = canvas.create_text(65, 12, text="Time Left: 60s", fill="#A6F6FF", font=("Times", 16, "italic"))
canvas.grid(row=1, column=1)  # We also have to pack our canvas

# Button to restart the app
style = Style()
style.configure('W.TButton', font=('Arial', 12, 'bold'), foreground='#6499E9')
restart_b = Button(text="Restart", style='W.TButton', command=restart)
restart_b.grid(row=1, column=2)

# Text Area to show the text the user needs to type in
text = Text(height=11, width=40, pady=10, padx=10, font=("Arial", 16, "italic"))
# Calling get_text to put some random text in this TextArea
get_text()
text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# User input to type the test
user_input = Entry(width=30, foreground="gray", justify=CENTER, font=("Arial", 16, "italic"))
user_input.insert(0, "Type the words here")
user_input.bind("<FocusIn>", on_entry_click)
user_input.bind("<FocusOut>", on_focus_out)
user_input.bind("<Key>", compare)
user_input.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Canvas to show results
canvas_result = Canvas(width=480, height=400, bg="white", highlightthickness=1)
cpm_score = canvas_result.create_text(190, 30, text="Your Score is: ", fill="black",
                                      font=("Times", 24, "bold"))
cpm_result = canvas_result.create_text(360, 30, text=f"{cpm} CPM ", fill="#6499E9",
                                       font=("Century Gothic", 24, "bold"))
wpm_score = canvas_result.create_text(210, 70, text="is equal to: ", fill="black",
                                      font=("Times", 18, "bold"))
wpm_result = canvas_result.create_text(310, 71, text=f"{wpm} WPM ", fill="#6499E9",
                                       font=("Century Gothic", 18, "bold"))

break_img = PhotoImage(file="break-time.png")
image_break = canvas_result.create_image(260, 150, image=break_img)  # Here we specify the position in X and Y

wrong_words = canvas_result.create_text(260, 220, text="", fill="#ff9966", font=("Times", 18, "bold"))
encourage_message = canvas_result.create_text(260, 250, text="", fill="#ff9966", font=("Times", 18, "bold"))

# Here we create a custom TextArea to be able to scroll through the mistakes
mistakes = TextScrollCombo(canvas_result)
mistakes.pack(fill="both", expand=True)
mistakes.config(width=450, height=120)
mistakes.txt.config(font=("consolas", 12), undo=True, wrap='word')
mistakes.txt.config(borderwidth=3, relief="sunken")
mistakes_window = canvas_result.create_window(245, 330, window=mistakes)

# In case the user don't make any mistake we will show an image
cons_im = PhotoImage(file="celebration.png")
congrats_im = canvas_result.create_image(245, 325, image=cons_im)  # Here we specify the position in X and Y

window.mainloop()
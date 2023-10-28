import pandas as pd
import textwrap
import shutil
import tkinter as tk
from tkinter import ttk



# column names
column_names = ['Subject', 'Predicate', 'Object']
df = pd.read_csv('Data\dictionary.csv', header=None, names=column_names)

# Get the terminal width
terminal_width, _ = shutil.get_terminal_size()

# brand name information extraction
def search_brand_info(brand_name):
    generic_name = None
    brand_type = None
    dosage_form = None
    strength = None
    manufacturer = None
    pharmacology_description = None
    side_effects_description = None

    brand_rows = df[df['Subject'] == brand_name]

    for _, row in brand_rows.iterrows():
        predicate = row['Predicate']
        obj = row['Object']
        if predicate == 'generic name is':
            generic_name = obj
        elif predicate == 'type of':
            brand_type = obj
        elif predicate == 'has dosage form':
            dosage_form = obj
        elif predicate == 'has strength of':
            strength = obj
        elif predicate == 'manufactured by':
            manufacturer = obj

    generic_rows = df[df['Subject'] == generic_name]
    for _, row in generic_rows.iterrows():
        predicate = row['Predicate']
        obj = row['Object']
        if predicate == 'pharmacology description':
            pharmacology_description = obj
        elif predicate == 'side effects':
            side_effects_description = obj

    brand_info = {
        'Brand Name': brand_name,
        'generic name is': generic_name,
        'type of': brand_type,
        'has dosage form': dosage_form,
        'has strength of': strength,
        'manufactured by': f'{manufacturer}\n',
        'pharmacology description': f'\n{textwrap.fill(pharmacology_description, width=terminal_width)}\n',
        'side effects': f'\n{textwrap.fill(side_effects_description, width=terminal_width)}'
    }

    return brand_info

# alternative brand extraction
def get_alternative_brands(brand_name, predicate):
    alternative_brands = []
    brand_rows = df[(df['Subject'] == brand_name) | (df['Object'] == brand_name)]
    
    for _, row in brand_rows.iterrows():
        if row['Predicate'] == predicate:
            alt_brand = row['Object'] if row['Subject'] == brand_name else row['Subject']
            alternative_brands.append(alt_brand)
    return alternative_brands

# format alternative brand output
def format_output(alternative_brands):
    formatted_output = "\n"
    max_length = max(len(name) for name in alternative_brands)

    for i, name in enumerate(alternative_brands, start=1):
        formatted_output += f"{i:2}. {name.ljust(max_length)}"
        if i % 2 == 0:
            formatted_output += "\n"
        else:
            formatted_output += "     "

    return formatted_output


# search any concept's info
def search_att_info(sub, pred):
    filtered = df[(df['Subject'] == sub) & (df['Predicate'] == pred)]
    if not filtered.empty:
        return filtered.iloc[0]['Object']
    else:
        return None


# query with a concept and relation
def two_input_query(subject, predicate):
    if predicate == 'pharmacology description':
        generic_name = search_att_info(subject, 'generic name is')
        generic_rows = df[(df['Subject'] == generic_name) & (df['Predicate'] == 'pharmacology description')]
        for _, row in generic_rows.iterrows():
            pharmacology_description = row['Object']
        output = f"Pharmacology Description:\n{textwrap.fill(pharmacology_description, width=terminal_width)}"
        
    elif predicate == 'side effects':
        generic_name = search_att_info(subject, 'generic name is')
        generic_rows = df[(df['Subject'] == generic_name) & (df['Predicate'] == 'side effects')]
        for _, row in generic_rows.iterrows():
            side_effects = row['Object']
        output = f"Side Effects:\n{textwrap.fill(side_effects, width=terminal_width)}"
        
    elif predicate == 'alternative brand':
        results = get_alternative_brands(subject, predicate)
        res = format_output(results)
        output = f"Alternative medicine brands for {subject}:\n{res}"
    
    elif predicate == 'generic name is':
        result = search_att_info(subject, predicate)
        output = f"Generic name of {subject}: {result}"
    
    elif predicate == 'type of':
        result = search_att_info(subject, predicate)
        output = f"Type of {subject}: {result}"
    
    elif predicate == 'has dosage form':
        result = search_att_info(subject, predicate)
        output = f"Dosage form of {subject}: {result}"
        
    elif predicate == 'has strength of':
        result = search_att_info(subject, predicate)
        output = f"Strength of {subject}: {result}"
    
    elif predicate == 'manufactured by':
        result = search_att_info(subject, predicate)
        output = f"{subject} is manufactured by: {result}"
        
    return output


# input transformation
def transform_input(input_str):
    middle_part = input_str[:input_str.index("(")]
    middle_part = middle_part.replace('_', ' ')
    
    if '(' in input_str and ')' in input_str:
        inner_content = input_str[input_str.index('(')+1:input_str.index(')')]
        parts = inner_content.split(', ')
        result_str = f"{parts[0]}, {middle_part}, {parts[1]}"
        return result_str
    else:
        return input_str 

# question answer
def question_answer(question):
    qu_ = transform_input(question)
    parts_ = qu_.split(', ')
    sub = parts_[0]
    pred = parts_[1]
    obj = parts_[2]
    
    if pred == 'pharmacology description' or pred == 'side effects':
        output_ = 'Invalid question!'
        return output_
    elif pred == 'alternative brand':
        if ((df['Subject'] == sub) & (df['Predicate'] == pred) & (df['Object'] == obj)).any():
            output_ = "Yes"
            return output_
        elif ((df['Subject'] == obj) & (df['Predicate'] == pred) & (df['Object'] == sub)).any():
            output_ = "Yes"
            return output_
        else:
            output_ = "No"
            return output_
    else:
        if ((df['Subject'] == sub) & (df['Predicate'] == pred) & (df['Object'] == obj)).any():
            output_ = "Yes"
            return output_
        else:
            output_ = "No"
            return output_


# clearing function
def clear_text_widgets():
    result_text.config(state='normal') 
    result_text.delete('1.0', tk.END)
    result_text.config(state='disabled')
    entry.delete('1.0', tk.END)


# Function to display info
def display_info():
    query = entry.get()
    
    if "(" in query and ")" in query:
        output_ = question_answer(query)
        
    elif "(" not in query and ")" not in query:
        input_values = query
        input_values = input_values.split(',')
        if len(input_values) == 1:
            brand_name = input_values[0].strip()
            result = search_brand_info(brand_name)
            if result:
                output_ = ""
                for key, value in result.items():
                    output_ += f"{key}: {value}\n"
            else:
                output_ = "Brand not found."
        elif len(input_values) == 2:
            sub = input_values[0].strip()
            pred = input_values[1].strip()
            output_ = two_input_query(sub, pred)
    
    # Update the result text widget with the output
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, output_)
    result_text.config(state='disabled')



# main application window
app = tk.Tk()
app.geometry("800x600")
app.title("Domain Specific Medicine Dictionary")


# back-ground color
app.configure(bg="lightblue")


# custom font
custom_font = ("Times New Roman", 14)


# entry field
label = tk.Label(app, text="Query Engine", font=custom_font)
label.pack(pady=8)
entry = tk.Entry(app, width=70, font=custom_font) 
entry.pack()


# search button
search_button = ttk.Button(app, text="Search", command=display_info)
search_button.pack(pady=10)


# text widget
result_text_frame = ttk.Frame(app)
result_text_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

result_text = tk.Text(result_text_frame, font=custom_font)
result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


# vertical scrollbar
scrollbar = ttk.Scrollbar(result_text_frame, command=result_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
result_text.config(yscrollcommand=scrollbar.set)

result_text.config(state='disabled')


# clear button
clear_button = tk.Button(app, text="Clear", command=clear_text_widgets)
clear_button.pack()


# run the application
app.mainloop()








input_file = 'insert.sql'
output_file = 'insertnew.sql'

with open(input_file, 'r') as file:
    content = file.read()

# Perform replacements
content = content.replace('Female', 'F')
content = content.replace('Male', 'M')
content = content.replace('Bigender', 'NB')
content = content.replace('Non-binary', 'NB')
content = content.replace('Genderfluid', 'NB')
content = content.replace('Genderqueer', 'NB')



with open(output_file, 'w') as file:
    file.write(content)
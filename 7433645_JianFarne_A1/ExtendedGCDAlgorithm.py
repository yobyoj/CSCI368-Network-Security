def extended_gcd(a, b):
    # Initialize variables for the Extended GCD algorithm
    n1, n2 = a, b
    a1, b1, a2, b2 = 1, 0, 0, 1
    rows = [(n1, n2, n1 // n2, n1 % n2, a1, b1, a2, b2)]

    while n2 != 0:
        q = n1 // n2
        n1, n2 = n2, n1 % n2
        a1, b1, a2, b2 = a2, b2, a1 - q * a2, b1 - q * b2
        rows.append((n1, n2, q, n1 % n2, a1, b1, a2, b2))

    return rows

def print_extended_gcd_table(rows):
    # Print the table of the Extended GCD algorithm
    print("\nExtended GCD Algorithm:")
    print("n1  n2  q  r  a1  b1  a2  b2")
    for row in rows:
        print("{:2}  {:2}  {:2}  {:2}  {:2}  {:2}  {:2}  {:2}".format(*row))

def main():
    try:
        # Input two integers
        a = int(input("Enter a: "))
        b = int(input("Enter b: "))

        # Run the Extended GCD algorithm
        rows = extended_gcd(a, b)

        # Display the results in the specified format
        print_extended_gcd_table(rows)

        # Display the summary
        summary = f"\nSummary:\ngcd({a}, {b}) = {rows[-2][1]}\n{a} * {rows[-2][5]} + {b} * {rows[-2][7]} = {rows[-2][1]}"
        print(summary)

    except ValueError:
        print("Invalid input. Please enter integers.")

if __name__ == "__main__":
    main()

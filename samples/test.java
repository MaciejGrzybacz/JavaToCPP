// Should work - basic product management
class ProductManager {
    private String productName;
    private double price;
    protected int quantity;
    public String category;

    public ProductManager(String productName, double price) {
        this.productName = productName;
        this.price = price;
        this.quantity = 0;
    }

    protected void updateInventory() {
        System.out.println("Updating inventory");
        List<Integer> quantities = new ArrayList<>();
        quantities.add(10);
        quantities.add(20);
        quantities.size();

        HashSet<String> categories = new HashSet<>();
        categories.add("electronics");
        categories.contains("electronics");

        HashMap<String, Double> prices = new HashMap<>();
        prices.put("discount", 0.9);
        prices.get("discount");
    }

    public void processOrder() {
        int ordered = 5;
        int available = 10;
        int processed = 0;

        for (int i = 0; i < ordered; i++) {
            System.out.println("Processing item: " + i);
        }

        if (ordered > available) {
            System.out.println("Not enough stock");
        } else {
            System.out.println("Order processed");
        }
    }

    private void setPrice(double price) {
        // Price update comment
        this.price = price;
        System.out.println("Price updated to: " + price);
    }
}

// Should work - basic banking operations
class BankAccount {
    private String accountNumber;
    private double balance;
    protected String accountType;
    public boolean isActive;

    public BankAccount(String accountNumber, String accountType) {
        this.accountNumber = accountNumber;
        this.accountType = accountType;
        this.balance = 0.0;
        this.isActive = true;
    }

    public void processTransactions() {
        List<Double> transactions = new ArrayList<>();
        transactions.add(100.0);
        transactions.add(-50.0);
        transactions.size();

        HashMap<String, Double> fees = new HashMap<>();
        fees.put("transfer", 1.0);
        fees.put("withdrawal", 2.0);

        HashSet<String> processedIds = new HashSet<>();
        processedIds.add("TX001");
        processedIds.contains("TX001");


        while (transactions.size() < 10) {
            System.out.println("Processing transaction...");
        }

        for (int i = 0; i < 5; i++) {
            System.out.println("Test: " + i);
        }
    }

    private void updateBalance(double amount) {
        // Update balance with validation
        this.balance += amount;
        System.out.println("Balance updated");
    }

    public double getBalance() {
        return balance;
    }
}

// Should NOT work - uses foreach and inheritance
class Animal {
    protected String name;

    public Animal(String name) {
        this.name = name;
    }

    public void makeSound() {
        System.out.println("Generic animal sound");
    }
}

class Zoo extends Animal {
    private List<String> animals;

    public Zoo(String name) {
        super(name);
        this.animals = new ArrayList<>();
    }

    public void addAnimals() {
        for (String animal : animals) {
            System.out.println("Added: " + animal);
        }
    }

    @Override
    public void makeSound() {
        System.out.println("Zoo sounds!");
    }
}

// Should NOT work - uses lambda and method reference
class DataProcessor {
    private List<Integer> numbers;

    public DataProcessor() {
        this.numbers = new ArrayList<>();
    }

    public void processNumbers() {
        numbers.forEach(n -> {
            System.out.println("Processing: " + n);
        });

        numbers.forEach(System.out::println);

        List<Integer> filtered = numbers.stream()
            .filter(n -> n > 0)
            .collect(Collectors.toList());
    }

    public void addNumber(int number) {
        numbers.add(number);
    }
}
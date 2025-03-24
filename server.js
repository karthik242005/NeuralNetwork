require("dotenv").config();
const express = require("express");
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const cors = require("cors");


// Debugging logs
console.log("✅ Starting server...");

// Check if environment variables are loaded
if (!process.env.PORT || !process.env.MONGO_URI || !process.env.JWT_SECRET) {
    console.error("❌ ERROR: Missing environment variables in .env file.");
    process.exit(1); // Stop execution
    console.log("PORT:", process.env.PORT);
    console.log("MONGO_URI:", process.env.MONGO_URI ? "Exists ✅" : "Missing ❌");
    console.log("JWT_SECRET:", process.env.JWT_SECRET ? "Exists ✅" : "Missing ❌");
}

const User = require("./models/User");

const app = express();
app.use(express.json());
app.use(cors());
app.use(express.static("public"));

// MongoDB Connection with Debug Logs
console.log("⏳ Connecting to MongoDB...");
mongoose.connect(process.env.MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
.then(() => console.log("✅ MongoDB connected!"))
.catch(err => {
    console.error("❌ MongoDB connection error:", err);
    process.exit(1);
});

// Test Route
app.get("/", (req, res) => {
    console.log("🔹 GET / request received.");
    res.send("🚀 Server is running!");
});

// User Signup Route
app.post("/signup", async (req, res) => {
    console.log("🔹 POST /signup request received:", req.body);
    const { username, email, password } = req.body;

    try {
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            console.warn("⚠️ User already exists:", email);
            return res.status(400).json({ error: "Email already exists" });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ username, email, password: hashedPassword });
        await newUser.save();

        console.log("✅ User registered successfully:", email);
        res.json({ message: "User registered successfully!" });
    } catch (err) {
        console.error("❌ Signup error:", err);
        res.status(500).json({ error: "Internal server error" });
    }
});

// User Login Route
app.post("/login", async (req, res) => {
    console.log("🔹 POST /login request received:", req.body);
    const { email, password } = req.body;

    try {
        const user = await User.findOne({ email });
        if (!user) {
            console.warn("⚠️ User not found:", email);
            return res.status(400).json({ error: "User not found" });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            console.warn("⚠️ Invalid password for:", email);
            return res.status(400).json({ error: "Invalid password" });
        }

        const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, { expiresIn: "1h" });

        console.log("✅ Login successful:", email);
        res.json({ message: "Login successful!", token });
    } catch (err) {
        console.error("❌ Login error:", err);
        res.status(500).json({ error: "Internal server error" });
    }
});

// Start Server with Debug Logs
app.listen(process.env.PORT, () => {
    console.log(`🚀 Server running on port ${process.env.PORT}`);
});


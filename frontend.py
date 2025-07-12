basic item listing:

import { useEffect, useState } from "react";
import axios from "../../services/api";

function ItemForm() {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    size: "",
    category: "",
    brand: "",
    condition_score: 3,
  });

  const [categories, setCategories] = useState([]);
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);

  useEffect(() => {
    // Fetch categories from backend
    const fetchCategories = async () => {
      const res = await axios.get("/api/categories/");
      setCategories(res.data);
    };
    fetchCategories();
  }, []);

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    setImages(files);

    // Previews
    const previews = files.map(file => URL.createObjectURL(file));
    setImagePreviews(previews);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // 1. Submit item details
      const itemRes = await axios.post("/api/items/", formData);
      const itemId = itemRes.data.id;

      // 2. Upload images
      for (let i = 0; i < images.length; i++) {
        const imgData = new FormData();
        imgData.append("item_id", itemId);
        imgData.append("image", images[i]);
        imgData.append("is_primary", i === 0); // First image is primary

        await axios.post("/api/upload-image/", imgData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }

      alert("Item listed successfully!");
      // Optional: Reset form
      setFormData({ title: "", description: "", size: "", category: "", brand: "", condition_score: 3 });
      setImages([]);
      setImagePreviews([]);
    } catch (err) {
      console.error(err);
      alert("Failed to list item.");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" placeholder="Title" value={formData.title} onChange={handleChange} required />
      <textarea name="description" placeholder="Description" value={formData.description} onChange={handleChange} />

      {/* Category Dropdown */}
      <select name="category" value={formData.category} onChange={handleChange} required>
        <option value="">Select Category</option>
        {categories.map(cat => (
          <option key={cat.id} value={cat.name}>{cat.name}</option>
        ))}
      </select>

      {/* Size Dropdown */}
      <select name="size" value={formData.size} onChange={handleChange} required>
        <option value="">Select Size</option>
        <option value="XS">XS</option>
        <option value="S">S</option>
        <option value="M">M</option>
        <option value="L">L</option>
        <option value="XL">XL</option>
      </select>

      <input name="brand" placeholder="Brand" value={formData.brand} onChange={handleChange} />

      {/* Condition Score */}
      <label>Condition (1 = Worn, 5 = Like New)</label>
      <input
        type="range"
        name="condition_score"
        min="1"
        max="5"
        value={formData.condition_score}
        onChange={handleChange}
      />
      <span>{formData.condition_score}/5</span>

      {/* Image Upload */}
      <input type="file" accept="image/*" multiple onChange={handleImageChange} />

      {/* Image Previews */}
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {imagePreviews.map((src, i) => (
          <img key={i} src={src} alt={preview-${i}} style={{ width: 100, height: 100, objectFit: "cover" }} />
        ))}
      </div>

      <button type="submit">List Item</button>
    </form>
  );
}

export default ItemForm;



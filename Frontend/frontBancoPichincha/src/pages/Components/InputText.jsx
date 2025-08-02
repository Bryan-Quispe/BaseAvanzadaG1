function InputText({ label, name, type = "text", value, onChange, required = false, pattern, title, placeholder }) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-semibold text-blue-900 mb-1" htmlFor={name}>
        {label} {required && "*"}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        required={required}
        pattern={pattern}
        title={title}
        placeholder={placeholder}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-yellow-400"
      />
    </div>
  );
}

export default InputText;
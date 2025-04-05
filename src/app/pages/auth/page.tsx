"use client";
import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useRouter } from "next/navigation";

const Page = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const router = useRouter();

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    router.push("/pages/otp"); // correct path assuming `otp/page.tsx` is under `app/otp`
  };

  const handleImageSubmit = () => {
    router.push("/pages/otp");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-800 to-indigo-900 flex items-center justify-center px-4">
      <Card className="w-full max-w-3xl min-h-[900px] rounded-2xl shadow-xl border-none">
        <CardContent className="p-10 space-y-10">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-800">GovAuth Portal</h1>
            <p className="text-base text-gray-500 mt-2">
              Verify yourself using Aadhaar
            </p>
          </div>

          {/* Aadhaar Number Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label
                htmlFor="mobile"
                className="block text-xl font-semibold text-gray-700 mb-3"
              >
                Aadhaar Number
              </label>
              <Input
                id="mobile"
                type="tel"
                pattern="[0-9]{10}"
                maxLength={10}
                placeholder="e.g. 9876543210"
                required
                className="bg-gray-100 text-2xl px-5 py-4 placeholder:text-2xl placeholder:text-gray-400 rounded-xl"
              />
            </div>

            <div className="flex justify-center">
              <Button
                type="submit"
                className="bg-amber-500 hover:bg-amber-600 text-white text-lg font-semibold rounded-full px-10 py-5 shadow-lg transition-all duration-200"
              >
                Get OTP
              </Button>
            </div>
          </form>

          {/* OR Divider */}
          <div className="relative">
            <div className="flex items-center justify-center my-6">
              <hr className="flex-grow border-gray-300" />
              <span className="mx-4 text-gray-500 font-medium">OR</span>
              <hr className="flex-grow border-gray-300" />
            </div>

            {/* Aadhaar Upload */}
            <div className="text-center">
              <label
                htmlFor="aadharUpload"
                className="inline-flex items-center gap-2 bg-white text-gray-700 border border-gray-300 rounded-full px-6 py-4 cursor-pointer hover:bg-gray-100 transition-all text-base font-medium"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-6 w-6 text-indigo-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M3 16l4-4m0 0l4 4m-4-4v12m8-2h3a2 2 0 002-2V7a2 2 0 00-2-2h-3.586a1 1 0 01-.707-.293l-1.414-1.414A2 2 0 0012.586 3H8a2 2 0 00-2 2v12"
                  />
                </svg>
                Upload Aadhaar Card
              </label>
              <input
                type="file"
                id="aadharUpload"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
              />
            </div>

            {/* Preview & Upload Button */}
            {selectedImage && (
              <div className="mt-6 text-center">
                <p className="text-base text-gray-600 mb-3 font-medium">
                  Aadhaar Preview:
                </p>
                <img
                  src={URL.createObjectURL(selectedImage)}
                  alt="Aadhaar Preview"
                  className="mx-auto rounded-lg shadow-md max-h-64 object-contain"
                />
                <Button
                  onClick={handleImageSubmit}
                  className="bg-amber-500 hover:bg-amber-600 text-white text-lg font-semibold rounded-full px-10 py-5 shadow-lg transition-all duration-200 mt-6"
                >
                  Upload Aadhaar Card
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Page;

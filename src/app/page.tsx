"use client";

import { Button } from "@/components/ui/button";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { CardContent, Card } from "@/components/ui/card";
import { Lock } from "lucide-react"; // Make sure lucide-react is installed

export default function Home() {
  const router = useRouter();

  const handleSubmit = () => {
    router.push("/pages/digilocker");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-800 to-indigo-900 flex items-center justify-center px-4">
      <Card className="w-full max-w-3xl min-h-[900px] rounded-2xl shadow-xl border-none bg-white">
        <CardContent className="p-10 space-y-10">
          {/* Heading */}
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-800">GovAuth Portal</h1>
            <p className="text-base text-gray-500 mt-2">
              Enter Aadhaar and verify using OTP
            </p>
          </div>

          {/* Aadhaar Card Image */}
          <div className="flex justify-center">
            <div className="border rounded-xl shadow-md overflow-hidden">
              <Image
                src="/dummy aadhar.png"
                alt="Aadhaar Card Preview"
                width={400}
                height={250}
                className="rounded-lg object-cover"
              />
            </div>
          </div>

          {/* Attention Text with Lock Icon */}
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600 font-medium">
            <Lock className="w-4 h-4 text-gray-500" />
            <span>Attention: Your data is encrypted & secure</span>
          </div>

          {/* Proceed Button */}
          <div className="pt-4">
            <Button
              onClick={handleSubmit}
              className="w-full bg-green-700 hover:bg-green-800 text-white py-4 rounded-xl text-lg shadow-lg transition"
            >
              PROCEED FOR KYC
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

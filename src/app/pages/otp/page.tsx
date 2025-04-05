"use client";
import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
  InputOTPSeparator,
} from "@/components/ui/input-otp";

const Page = () => {
  const [otp, setOtp] = useState("");

  const handleSubmit = () => {
    if (otp.length === 6) {
      alert("OTP Verified ✅");
      // You can navigate or trigger verification here
    } else {
      alert("Please enter all 6 digits of the OTP.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-800 to-indigo-900 flex items-center justify-center px-4">
      <Card className="w-full max-w-xl min-h-[600px] rounded-2xl shadow-2xl border-none">
        <CardContent className="p-10 flex flex-col items-center justify-center space-y-10">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-black ">OTP Verification</h1>
            <p className="text-gray-500 mt-2">
              Enter the 6-digit OTP sent to your number
            </p>
          </div>

          <InputOTP
            maxLength={6}
            value={otp}
            onChange={(val) => setOtp(val)}
            className="scale-110"
          >
            <InputOTPGroup>
              <InputOTPSlot
                index={0}
                className="w-16 h-16 text-2xl rounded-lg"
              />
              <InputOTPSlot
                index={1}
                className="w-16 h-16 text-2xl rounded-lg"
              />
              <InputOTPSlot
                index={2}
                className="w-16 h-16 text-2xl rounded-lg"
              />
            </InputOTPGroup>
            <InputOTPSeparator />
            <InputOTPGroup>
              <InputOTPSlot
                index={3}
                className="w-16 h-16 text-2xl rounded-lg"
              />
              <InputOTPSlot
                index={4}
                className="w-16 h-16 text-2xl rounded-lg"
              />
              <InputOTPSlot
                index={5}
                className="w-16 h-16 text-2xl rounded-lg"
              />
            </InputOTPGroup>
          </InputOTP>

          <Button
            onClick={handleSubmit}
            className="mt-6 bg-amber-500 hover:bg-amber-600 text-white text-base font-semibold rounded-full px-8 py-4 shadow-lg transition-all"
          >
            Verify OTP
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default Page;
